from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore

app = 