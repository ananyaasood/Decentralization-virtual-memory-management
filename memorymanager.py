import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Module 1: Distributed Memory Manager (Core) ---
class Node:
    def __init__(self, node_id, memory_size):
        self.node_id = node_id
        self.memory = pd.DataFrame(columns=['page_id', 'data', 'access_count'])
        self.memory_size = memory_size

    def allocate_page(self, page_id, data):
        if len(self.memory) < self.memory_size:
            self.memory.loc[len(self.memory)] = [page_id, data, 0]
            return True
        return False  # Memory full

    def access_page(self, page_id):
        page = self.memory[self.memory['page_id'] == page_id]
        if not page.empty:
            self.memory.loc[page.index, 'access_count'] += 1
            return page.iloc[0]['data']
        return None  # Page fault

# Initialize 3 nodes
nodes = [Node(i, 3) for i in range(3)]

# Distribute pages (simplified hashing)
pages = [(f'page_{i}', f'data_{i}') for i in range(10)]
for page_id, data in pages:
    node_idx = hash(page_id) % 3
    if not nodes[node_idx].allocate_page(page_id, data):
        print(f"Node {node_idx} full! Page {page_id} not allocated.")

# --- Module 2: Security (Simplified) ---
def encrypt(data, key=0x55):
    data_bytes = data.encode()
    encrypted = np.array([b ^ key for b in data_bytes], dtype=np.uint8)
    return encrypted.tobytes()

def decrypt(encrypted_data, key=0x55):
    decrypted = np.frombuffer(encrypted_data, dtype=np.uint8)
    return bytes([b ^ key for b in decrypted]).decode()

# --- Module 3: Monitoring ---
def plot_access_stats():
    stats = pd.concat([node.memory for node in nodes])
    access_counts = stats.groupby('page_id')['access_count'].sum().sort_values()
    
    fig, ax = plt.subplots()
    access_counts.plot(kind='bar', ax=ax, title='Page Access Frequency')
    ax.set_xlabel('Page ID')
    ax.set_ylabel('Access Counts')
    return fig

# --- Module 4: GUI (tkinter) ---
class MemoryManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Decentralized Virtual Memory Manager")
        
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")
        
        # Tab 1: Node Status
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Node Status")
        self.setup_node_status_tab()
        
        # Tab 2: Page Access
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Page Access")
        self.setup_page_access_tab()
        
        # Tab 3: Security Demo
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Security Demo")
        self.setup_security_tab()
        
        # Tab 4: Monitoring
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="Monitoring")
        self.setup_monitoring_tab()
    
    def setup_node_status_tab(self):
        for node in nodes:
            frame = ttk.LabelFrame(self.tab1, text=f"Node {node.node_id}")
            frame.pack(padx=10, pady=5, fill="x")
            
            ttk.Label(frame, text=f"Memory Usage: {len(node.memory)}/{node.memory_size}").pack()
            if not node.memory.empty:
                tree = ttk.Treeview(frame, columns=('Page ID', 'Data', 'Access Count'), show='headings')
                tree.heading('Page ID', text='Page ID')
                tree.heading('Data', text='Data')
                tree.heading('Access Count', text='Access Count')
                for _, row in node.memory.iterrows():
                    tree.insert('', 'end', values=(row['page_id'], row['data'], row['access_count']))
                tree.pack()
    
    def setup_page_access_tab(self):
        ttk.Label(self.tab2, text="Enter Page ID:").pack(pady=5)
        self.page_entry = ttk.Entry(self.tab2)
        self.page_entry.pack(pady=5)
        
        ttk.Button(self.tab2, text="Access Page", command=self.access_page).pack(pady=5)
        self.result_label = ttk.Label(self.tab2, text="")
        self.result_label.pack(pady=5)
    
    def access_page(self):
        page_id = self.page_entry.get()
        for node in nodes:
            data = node.access_page(page_id)
            if data is not None:
                self.result_label.config(text=f"Page '{page_id}' found in Node {node.node_id}: {data}")
                return
        self.result_label.config(text=f"Page '{page_id}' not found (Page Fault)!")
    
    def setup_security_tab(self):
        ttk.Label(self.tab3, text="Enter Data to Encrypt:").pack(pady=5)
        self.data_entry = ttk.Entry(self.tab3)
        self.data_entry.pack(pady=5)
        
        ttk.Button(self.tab3, text="Encrypt & Decrypt", command=self.demo_security).pack(pady=5)
        self.security_label = ttk.Label(self.tab3, text="")
        self.security_label.pack(pady=5)
    
    def demo_security(self):
        data = self.data_entry.get()
        encrypted = encrypt(data)
        decrypted = decrypt(encrypted)
        self.security_label.config(text=f"Original: {data}\nEncrypted: {encrypted}\nDecrypted: {decrypted}")
    
    def setup_monitoring_tab(self):
        fig = plot_access_stats()
        canvas = FigureCanvasTkAgg(fig, self.tab4)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryManagerGUI(root)
    root.mainloop()