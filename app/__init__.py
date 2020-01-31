from flask import Flask
import os
app = Flask(__name__);
from app import routes
app._static_folder_ = os.path.abspath('templates/static');