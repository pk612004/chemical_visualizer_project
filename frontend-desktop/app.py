
"""
Chemical Equipment Visualizer - PyQt5 desktop frontend
Features:
 - Login / Signup (token auth)
 - Choose CSV and upload to Django REST API
 - Fetch history (last uploads)
 - Load CSV into a QTableWidget
 - Show charts: pie (type distribution) + bar (averages)
 - Download PDF report for a selected history item
 - Basic token persistence (~/.chemical_visualizer_token)
"""

import sys
import os
import json
import io
import requests
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QTextEdit, QLineEdit, QHBoxLayout, QListWidget, QListWidgetItem,
    QSplitter, QTableWidget, QTableWidgetItem, QMessageBox, QSizePolicy,
    QFrame
)
from PyQt5.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE = os.environ.get('API_BASE', 'http://127.0.0.1:8000/api/')
TOKEN_STORE = os.path.expanduser('~/.chemical_visualizer_token')
REQUEST_TIMEOUT = 10 


def save_token_to_disk(token):
    try:
        with open(TOKEN_STORE, 'w') as f:
            f.write(token)
    except Exception:
        pass


def load_token_from_disk():
    try:
        if os.path.exists(TOKEN_STORE):
            with open(TOKEN_STORE, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return None


def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return None


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chemical Equipment Visualizer (Desktop)')
        self.setMinimumSize(QSize(1000, 700))

        self.token = load_token_from_disk()
        self.filepath = None
        self.history = []  

        root = QVBoxLayout()
        header = QLabel('<h2>Chemical Equipment Visualizer</h2>')
        root.addWidget(header)

        auth_row = QHBoxLayout()
        self.username = QLineEdit(); self.username.setPlaceholderText('username')
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.Password); self.password.setPlaceholderText('password')
        self.btn_login = QPushButton('Login'); self.btn_login.clicked.connect(self.login)
        self.btn_signup = QPushButton('Sign up'); self.btn_signup.clicked.connect(self.signup)
        self.btn_logout = QPushButton('Logout'); self.btn_logout.clicked.connect(self.logout)
        auth_row.addWidget(QLabel('Auth:'))
        auth_row.addWidget(self.username)
        auth_row.addWidget(self.password)
        auth_row.addWidget(self.btn_login)
        auth_row.addWidget(self.btn_signup)
        auth_row.addWidget(self.btn_logout)
        root.addLayout(auth_row)

        splitter = QSplitter(Qt.Horizontal)

        left_frame = QFrame()
        left_layout = QVBoxLayout()

        upload_row = QHBoxLayout()
        self.btn_choose = QPushButton('Choose CSV'); self.btn_choose.clicked.connect(self.choose)
        self.lbl_chosen = QLabel('No file chosen')
        self.btn_upload = QPushButton('Upload to server'); self.btn_upload.clicked.connect(self.upload)
        upload_row.addWidget(self.btn_choose)
        upload_row.addWidget(self.lbl_chosen)
        upload_row.addWidget(self.btn_upload)
        left_layout.addLayout(upload_row)

        summary_label = QLabel('<b>Summary</b>')
        left_layout.addWidget(summary_label)
        self.summary_text = QTextEdit(); self.summary_text.setReadOnly(True); self.summary_text.setMaximumHeight(120)
        left_layout.addWidget(self.summary_text)

        self.figure = Figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(self.canvas, 1)

        table_label = QLabel('<b>CSV Table</b>')
        left_layout.addWidget(table_label)
        self.table = QTableWidget()
        left_layout.addWidget(self.table, 2)

        left_frame.setLayout(left_layout)
        splitter.addWidget(left_frame)

        right_frame = QFrame()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel('<b>History (last uploads)</b>'))
        self.lst_history = QListWidget()
        self.lst_history.itemDoubleClicked.connect(self.on_history_double)
        right_layout.addWidget(self.lst_history)
        btns_row = QHBoxLayout()
        self.btn_load_selected = QPushButton('Load selected'); self.btn_load_selected.clicked.connect(self.load_selected_history)
        self.btn_download_pdf = QPushButton('Download PDF for selected'); self.btn_download_pdf.clicked.connect(self.download_pdf_for_selected)
        btns_row.addWidget(self.btn_load_selected)
        btns_row.addWidget(self.btn_download_pdf)
        right_layout.addLayout(btns_row)
        right_layout.addStretch()
        right_frame.setLayout(right_layout)
        right_frame.setMaximumWidth(380)
        splitter.addWidget(right_frame)

        root.addWidget(splitter)

        # log area
        root.addWidget(QLabel('<b>Log</b>'))
        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(160)
        root.addWidget(self.log)

        self.setLayout(root)


        self._update_auth_ui()
        self.fetch_history()  

    def _update_auth_ui(self):
        if self.token:
            self.log_msg('Authenticated (token present).')
            self.btn_login.setEnabled(False)
            self.btn_signup.setEnabled(False)
            self.btn_logout.setEnabled(True)
            self.username.setEnabled(False)
            self.password.setEnabled(False)
        else:
            self.log_msg('Not authenticated.')
            self.btn_login.setEnabled(True)
            self.btn_signup.setEnabled(True)
            self.btn_logout.setEnabled(False)
            self.username.setEnabled(True)
            self.password.setEnabled(True)

    def log_msg(self, s):
        ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
        self.log.append(f'[{ts}] {s}')

    def login(self):
        user = self.username.text().strip(); pwd = self.password.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, 'Login', 'Enter username and password')
            return
        try:
            url = API_BASE + 'auth/api-token-auth/'
            self.log_msg(f'POST {url} (form)')
            res = requests.post(url, data={'username': user, 'password': pwd}, timeout=REQUEST_TIMEOUT)
            if res.status_code in (200, 201) and 'token' in res.text:
                j = safe_json(res) or {}
                token = j.get('token') or j.get('auth_token') or j.get('key')
                if token:
                    self.token = token
                    save_token_to_disk(token)
                    self.log_msg('Login OK. Token saved.')
                    self._update_auth_ui()
                    self.fetch_history()
                    return
            self.log_msg('Form login did not return token; trying JSON payload.')
            res2 = requests.post(url, json={'username': user, 'password': pwd}, timeout=REQUEST_TIMEOUT)
            j = safe_json(res2) or {}
            token = j.get('token') or j.get('auth_token') or j.get('key')
            if token:
                self.token = token
                save_token_to_disk(token)
                self.log_msg('Login OK (JSON). Token saved.')
                self._update_auth_ui()
                self.fetch_history()
                return
            self.log_msg(f'Login failed: status {res.status_code} / {res2.status_code} : {res.text} {res2.text}')
            QMessageBox.warning(self, 'Login failed', f'Status: {res.status_code} / {res2.status_code}\n{res.text}\n{res2.text}')
        except Exception as e:
            self.log_msg('Login exception: ' + str(e))
            QMessageBox.critical(self, 'Login error', str(e))

    def signup(self):
        user = self.username.text().strip(); pwd = self.password.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, 'Signup', 'Enter username and password to sign up')
            return
        try:
            url = API_BASE + 'register/'
            self.log_msg(f'POST {url} (form)')
            res = requests.post(url, data={'username': user, 'password': pwd}, timeout=REQUEST_TIMEOUT)
            j = safe_json(res) or {}
            token = j.get('token') or j.get('auth_token') or j.get('key')
            if token:
                self.token = token
                save_token_to_disk(token)
                self.log_msg('Signup OK (form). Token saved.')
                self._update_auth_ui()
                self.fetch_history()
                return
            res2 = requests.post(url, json={'username': user, 'password': pwd}, timeout=REQUEST_TIMEOUT)
            j2 = safe_json(res2) or {}
            token2 = j2.get('token') or j2.get('auth_token') or j2.get('key')
            if token2:
                self.token = token2
                save_token_to_disk(token2)
                self.log_msg('Signup OK (json). Token saved.')
                self._update_auth_ui()
                self.fetch_history()
                return
            self.log_msg(f'Signup failed: {res.status_code} {res.text} {res2.status_code if "res2" in locals() else ""}')
            QMessageBox.warning(self, 'Signup failed', f'{res.text}')
        except Exception as e:
            self.log_msg('Signup exception: ' + str(e))
            QMessageBox.critical(self, 'Signup error', str(e))

    def logout(self):
        self.token = None
        try:
            if os.path.exists(TOKEN_STORE):
                os.remove(TOKEN_STORE)
        except Exception:
            pass
        self._update_auth_ui()
        self.log_msg('Logged out (token cleared).')

    def choose(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open CSV', filter='CSV Files (*.csv)')
        if path:
            self.filepath = path
            self.lbl_chosen.setText(os.path.basename(path))
            self.log_msg(f'Chosen: {path}')

    def upload(self):
        if not self.filepath:
            QMessageBox.warning(self, 'Upload', 'No file chosen')
            return
        if not self.token:
            QMessageBox.warning(self, 'Upload', 'Not logged in. Please login first.')
            return
        try:
            url = API_BASE + 'upload/'
            headers = {'Authorization': f'Token {self.token}'}
            self.log_msg(f'Uploading {self.filepath} -> {url}')
            with open(self.filepath, 'rb') as fh:
                files = {'file': (os.path.basename(self.filepath), fh, 'text/csv')}
                resp = requests.post(url, files=files, data={'name': os.path.basename(self.filepath)}, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code in (200, 201):
                j = safe_json(resp) or {}
                summary = j.get('summary') or j.get('summary_json') or j.get('summary_json', {})
                self.log_msg('Upload OK. Server returned summary.')
                try:
                    pretty = json.dumps(summary, indent=2)
                    self.summary_text.setPlainText(f"Total rows: {summary.get('total', 'N/A')}\nAverages: {pretty}")
                except Exception:
                    self.summary_text.setPlainText(str(summary))
                # plot
                if summary:
                    self.plot_summary(summary)
                self.fetch_history()
            else:
                self.log_msg('Upload failed: ' + resp.text[:1000])
                QMessageBox.warning(self, 'Upload failed', f'{resp.status_code}\n{resp.text}')
        except Exception as e:
            self.log_msg('Upload exception: ' + str(e))
            QMessageBox.critical(self, 'Upload error', str(e))

    def fetch_history(self):
        if not self.token:
            self.log_msg('Skipping history fetch: not authenticated.')
            return
        try:
            url = API_BASE + 'history/'
            headers = {'Authorization': f'Token {self.token}'}
            self.log_msg(f'GET {url}')
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                arr = safe_json(resp) or []
                self.history = arr
                self.populate_history_list()
                self.log_msg(f'History fetched: {len(arr)} entries')
            else:
                self.log_msg('History fetch failed: ' + resp.text)
        except Exception as e:
            self.log_msg('History exception: ' + str(e))

    def populate_history_list(self):
        self.lst_history.clear()
        for item in self.history:
            name = item.get('name') or item.get('csv_url') or 'unnamed'
            uploaded = item.get('uploaded_at') or ''
            try:
                uploaded_fmt = datetime.fromisoformat(uploaded.replace('Z', '+00:00')).strftime('%c') if uploaded else ''
            except Exception:
                uploaded_fmt = uploaded
            text = f"{name}\n{uploaded_fmt}\nID: {item.get('id')}"
            lw = QListWidgetItem(text)
            lw.setData(Qt.UserRole, item)
            self.lst_history.addItem(lw)

    def on_history_double(self, item):
        self.load_history_item(item.data(Qt.UserRole))

    def load_selected_history(self):
        item = self.lst_history.currentItem()
        if not item:
            QMessageBox.information(self, 'Select', 'Select an entry first.')
            return
        self.load_history_item(item.data(Qt.UserRole))

    def load_history_item(self, record):
        """
        record: dict from history endpoint, should contain id and csv_url (or we fetch csv via server)
        """
        if not record:
            return
        self.log_msg(f'Loading history item id={record.get("id")}')
 
        csv_url = record.get('csv_url') or record.get('file') or None
        headers = {'Authorization': f'Token {self.token}'} if self.token else {}
        try:
            if csv_url:
              
                if csv_url.startswith('/'):
                    csv_url_full = csv_url if csv_url.startswith('http') else API_BASE.rstrip('/') + csv_url
                else:
                    csv_url_full = csv_url if csv_url.startswith('http') else API_BASE + csv_url
                self.log_msg(f'GET CSV {csv_url_full}')
                r = requests.get(csv_url_full, headers=headers, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    df = pd.read_csv(io.StringIO(r.text))
                    self.populate_table(df)
                else:
                    self.log_msg('CSV download failed, trying server summary endpoint...')
                    self._load_from_summary(record)
            else:
                
                self._load_from_summary(record)
        except Exception as e:
            self.log_msg('Load history exception: ' + str(e))
            self._load_from_summary(record)

    def _load_from_summary(self, record):

        try:
            pid = record.get('id')
            if pid is None:
                self.log_msg('No id for record')
                return
            url = API_BASE + f'summary/{pid}/' 
            headers = {'Authorization': f'Token {self.token}'} if self.token else {}
            self.log_msg(f'Trying {url}')
            r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                j = safe_json(r) or {}
                summary = j.get('summary') or j
                self.plot_summary(summary)
                self.summary_text.setPlainText(json.dumps(summary, indent=2))
            else:
                self.log_msg('Summary endpoint not available or failed.')
        except Exception as e:
            self.log_msg('Summary fetch exception: ' + str(e))


    def plot_summary(self, summary):

        if not summary:
            self.log_msg('No summary to plot.')
            return
        try:
            self.figure.clear()
            ax1 = self.figure.add_subplot(121)
            ax2 = self.figure.add_subplot(122)

            type_dist = summary.get('type_distribution') or summary.get('typeDistribution') or {}
            avgs = summary.get('averages') or summary.get('avg') or {}

            if isinstance(type_dist, dict) and len(type_dist) > 0:
                labels = list(type_dist.keys())
                sizes = list(type_dist.values())
                ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
                ax1.set_title('Type distribution')
            else:
                ax1.text(0.5, 0.5, 'No type distribution', ha='center', va='center')
                ax1.set_axis_off()

            if isinstance(avgs, dict) and len(avgs) > 0:
                labels = list(avgs.keys())
                vals = [float(avgs[k]) for k in labels]
                ax2.bar(labels, vals)
                ax2.set_title('Averages')
            else:
                ax2.text(0.5, 0.5, 'No averages', ha='center', va='center')
                ax2.set_axis_off()

            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            self.log_msg('Plotting error: ' + str(e))

    def populate_table(self, df: pd.DataFrame):
        try:
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            rows, cols = df.shape
            self.table.setRowCount(rows)
            self.table.setColumnCount(cols)
            self.table.setHorizontalHeaderLabels(list(df.columns.astype(str)))
            for r in range(rows):
                for c in range(cols):
                    val = df.iat[r, c]
                    item = QTableWidgetItem(str(val))
                    self.table.setItem(r, c, item)
            self.log_msg(f'Table loaded: {rows} rows x {cols} cols')
        except Exception as e:
            self.log_msg('Populate table error: ' + str(e))

    # === PDF download ===
    def download_pdf_for_selected(self):
        item = self.lst_history.currentItem()
        if not item:
            QMessageBox.information(self, 'Select', 'Select an entry first.')
            return
        record = item.data(Qt.UserRole)
        pid = record.get('id')
        if not pid:
            QMessageBox.warning(self, 'PDF', 'No id for selected record.')
            return
        try:
            url = API_BASE + f'generate_pdf/{pid}/'
            headers = {'Authorization': f'Token {self.token}'} if self.token else {}
            self.log_msg(f'GET {url} (download PDF)')
            r = requests.get(url, headers=headers, stream=True, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                fname = f'report_{pid}.pdf'
                with open(fname, 'wb') as fh:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            fh.write(chunk)
                self.log_msg(f'PDF saved as {fname}')
                QMessageBox.information(self, 'PDF Downloaded', f'Saved {fname}')
            else:
                self.log_msg(f'PDF request failed: {r.status_code} {r.text}')
                QMessageBox.warning(self, 'PDF failed', f'{r.status_code} {r.text}')
        except Exception as e:
            self.log_msg('PDF download error: ' + str(e))
            QMessageBox.critical(self, 'PDF error', str(e))

    def download_pdf(self):
  
        if not self.history:
            QMessageBox.information(self, 'PDF', 'No history available.')
            return
        record = self.history[0]
        self.download_pdf_for_record(record)

    def download_pdf_for_record(self, record):
  
        pid = record.get('id')
        if not pid:
            self.log_msg('Record missing id for PDF download.')
            return
        url = API_BASE + f'generate_pdf/{pid}/'
        headers = {'Authorization': f'Token {self.token}'} if self.token else {}
        try:
            r = requests.get(url, headers=headers, stream=True, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                fname = f'report_{pid}.pdf'
                with open(fname, 'wb') as fh:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            fh.write(chunk)
                self.log_msg(f'PDF saved as {fname}')
                QMessageBox.information(self, 'Saved', fname)
            else:
                self.log_msg(f'PDF failed: {r.status_code} {r.text}')
                QMessageBox.warning(self, 'PDF failed', f'{r.status_code} {r.text}')
        except Exception as e:
            self.log_msg('PDF exception: ' + str(e))
            QMessageBox.critical(self, 'PDF error', str(e))
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
