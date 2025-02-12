from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import json
import urllib3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CyberPanel Configuration
BASE_URL = "https://80.225.216.193:8090"
ADMIN_USER = "devadmin"
ADMIN_PASS = "e@6bqgnm!A0c1x1P"
HEADERS = {"Content-Type": "application/json"}

def cyberpanel_api(endpoint, payload):
    url = f"{BASE_URL}/api/{endpoint}"
    try:
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=HEADERS,
            verify=False
        )
        # Debug prints to help diagnose any JSON or HTML response:
        print("=== DEBUG ===")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        print("=============")
        return response.json()  # Convert response to JSON (if valid)
    except Exception as e:
        print("Exception in cyberpanel_api:", e)
        return {"error": str(e)}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Website Management Routes
@app.route('/create_website', methods=['POST'])
def create_website():
    payload = {
        "adminUser": ADMIN_USER,
        "adminPass": ADMIN_PASS,
        "domainName": request.form['domain'],
        "ownerEmail": request.form['email'],
        # Default to 'Default' package if user does not provide or keep it from form:
        "packageName": request.form.get('package', 'Default'),
        "websiteOwner": request.form['owner'],
        "ownerPassword": request.form['password'],
        "phpVersion": request.form['phpVersion']
    }
    response = cyberpanel_api('createWebsite', payload)
    # Show a flash message based on success/failure:
    flash(
        response.get('errorMessage') or 'Website created successfully!',
        'success' if response.get('status') == 1 else 'danger'
    )
    return redirect(url_for('index'))

@app.route('/delete_website', methods=['POST'])
def delete_website():
    payload = {
        "adminUser": ADMIN_USER,
        "adminPass": ADMIN_PASS,
        "domainName": request.form['domain']
    }
    response = cyberpanel_api('deleteWebsite', payload)
    flash(
        response.get('errorMessage') or 'Website deleted successfully!',
        'success' if response.get('status') == 1 else 'danger'
    )
    return redirect(url_for('index'))

@app.route('/change_package', methods=['POST'])
def change_package():
    payload = {
        "adminUser": ADMIN_USER,
        "adminPass": ADMIN_PASS,
        "websiteName": request.form['website'],
        "packageName": request.form['package']
    }
    response = cyberpanel_api('changePackageAPI', payload)
    flash(
        response.get('errorMessage') or 'Package updated successfully!',
        'success' if response.get('status') == 1 else 'danger'
    )
    return redirect(url_for('index'))

@app.route('/submit_status', methods=['POST'])
def submit_status():
    payload = {
        "adminUser": ADMIN_USER,
        "adminPass": ADMIN_PASS,
        "websiteName": request.form['website'],
        "state": request.form['state']
    }
    response = cyberpanel_api('submitWebsiteStatus', payload)
    flash(
        response.get('errorMessage') or 'Status updated successfully!',
        'success' if response.get('status') == 1 else 'danger'
    )
    return redirect(url_for('index'))

# User Management Routes
@app.route('/create_user', methods=['POST'])
def create_user():
    payload = {
        "adminUser": ADMIN_USER,
        "adminPass": ADMIN_PASS,
        "firstName": request.form['first_name'],
        "lastName": request.form['last_name'],
        "email": request.form['email'],
        "userName": request.form['username'],
        "password": request.form['password'],
        "websitesLimit": request.form['limit'],
        "selectedACL": request.form['acl'],
        "securityLevel": request.form['security_level']
    }
    response = cyberpanel_api('submitUserCreation', payload)
    flash(
        response.get('errorMessage') or 'User created successfully!',
        'success' if response.get('status') == 1 else 'danger'
    )
    return redirect(url_for('index'))

@app.route('/get_user_info', methods=['POST'])
def get_user_info():
    payload = {
        "adminUser": ADMIN_USER,
        "adminPass": ADMIN_PASS,
        "username": request.form['username']
    }
    response = cyberpanel_api('getUserInfo', payload)
    session['user_info'] = response
    return redirect(url_for('index'))

@app.route('/change_password', methods=['POST'])
def change_password():
    payload = {
        "adminUser": ADMIN_USER,
        "adminPass": ADMIN_PASS,
        "websiteOwner": request.form['username'],
        "ownerPassword": request.form['password']
    }
    response = cyberpanel_api('changeUserPassAPI', payload)
    flash(
        response.get('errorMessage') or 'Password changed successfully!',
        'success' if response.get('status') == 1 else 'danger'
    )
    return redirect(url_for('index'))

# System Routes
@app.route('/add_firewall_rule', methods=['POST'])
def add_firewall_rule():
    payload = {
        "adminUser": ADMIN_USER,
        "adminPass": ADMIN_PASS,
        "ruleName": request.form['name'],
        "ruleProtocol": request.form['protocol'],
        "rulePort": request.form['port'],
        "ruleIP": request.form['ip']
    }
    response = cyberpanel_api('addFirewallRule', payload)
    flash(
        response.get('errorMessage') or 'Firewall rule added successfully!',
        'success' if response.get('status') == 1 else 'danger'
    )
    return redirect(url_for('index'))

@app.route('/verify_connection', methods=['POST'])
def verify_connection():
    payload = {
        "adminUser": ADMIN_USER,
        "adminPass": ADMIN_PASS
    }
    response = cyberpanel_api('verifyConn', payload)
    flash(f"Connection Status: {response.get('statusMessage', 'Unknown status')}", 'info')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    url = f"{BASE_URL}/api/loginAPI"
    payload = {
        "username": request.form['username'],
        "password": request.form['password']
    }
    try:
        response = requests.post(url, data=payload, verify=False)
        result = response.json()
        flash(f"Login Status: {result.get('errorMessage', 'Success')}", 'info')
    except Exception as e:
        flash(f"Login Error: {str(e)}", 'danger')
    return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)
