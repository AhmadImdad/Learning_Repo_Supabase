from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from supabase import create_client, Client
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Password configuration
REQUIRED_PASSWORD = os.environ.get('REQUIRED_PASSWORD')

# Supabase configuration - using environment variables for security
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Password login template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Links - Access Required</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 60px 40px;
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
            font-size: 2.5em;
            font-weight: 300;
        }
        .subtitle {
            color: #666;
            margin-bottom: 40px;
            font-size: 1.1em;
        }
        .form-group {
            margin-bottom: 30px;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 10px;
            color: #555;
            font-weight: 600;
            font-size: 1.1em;
        }
        input[type="password"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1.1em;
            transition: border-color 0.3s ease;
            box-sizing: border-box;
        }
        input[type="password"]:focus {
            outline: none;
            border-color: #4CAF50;
        }
        .btn {
            padding: 15px 40px;
            font-size: 1.2em;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            width: 100%;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        .flash-messages {
            margin-bottom: 30px;
        }
        .flash-error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 5px solid #dc3545;
        }
        .lock-icon {
            font-size: 3em;
            margin-bottom: 20px;
            color: #667eea;
        }
        .required {
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="lock-icon">🔒</div>
        <h1>Learning Links</h1>
        <p class="subtitle">Please enter the password to continue</p>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="form-group">
                <label for="password">Password <span class="required">*</span></label>
                <input type="password" id="password" name="password" required placeholder="Enter password">
            </div>
            <button type="submit" class="btn">🔓 Access Learning Links</button>
        </form>
    </div>
</body>
</html>
"""

# Main page template with buttons
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Links Database Manager</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 60px 40px;
            text-align: center;
            max-width: 500px;
            width: 90%;
        }
        h1 {
            color: #333;
            margin-bottom: 40px;
            font-size: 2.5em;
            font-weight: 300;
        }
        .subtitle {
            color: #666;
            margin-bottom: 50px;
            font-size: 1.1em;
        }
        .button-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .btn {
            padding: 20px 40px;
            font-size: 1.2em;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .btn-primary {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }
        .btn-secondary {
            background: linear-gradient(45deg, #2196F3, #1976D2);
            color: white;
        }
        .btn-logout {
            background: linear-gradient(45deg, #f44336, #d32f2f);
            color: white;
            font-size: 1em;
            padding: 10px 20px;
            margin-top: 30px;
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        .flash-messages {
            margin-bottom: 30px;
        }
        .flash-success {
            background-color: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 5px solid #28a745;
        }
        .flash-error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 5px solid #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Learning Links</h1>
        <p class="subtitle">Manage your important learning resources</p>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        <div class="button-container">
            <a href="{{ url_for('add_entry') }}" class="btn btn-primary">
                ➕ Add New Entry
            </a>
            <a href="{{ url_for('show_records') }}" class="btn btn-secondary">
                📋 Show All Records
            </a>
        </div>
        
        <a href="{{ url_for('logout') }}" class="btn btn-logout">
            🚪 Logout
        </a>
    </div>
</body>
</html>
"""

# Add entry form template
ADD_ENTRY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add New Learning Link</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.2em;
            font-weight: 300;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
            font-size: 1.1em;
        }
        input[type="text"], input[type="url"], textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s ease;
            box-sizing: border-box;
        }
        input[type="text"]:focus, input[type="url"]:focus, textarea:focus {
            outline: none;
            border-color: #4CAF50;
        }
        textarea {
            resize: vertical;
            min-height: 120px;
        }
        .button-group {
            display: flex;
            gap: 15px;
            justify-content: space-between;
            margin-top: 40px;
        }
        .btn {
            padding: 15px 30px;
            font-size: 1.1em;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            flex: 1;
            text-align: center;
        }
        .btn-submit {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }
        .btn-back {
            background: linear-gradient(45deg, #9E9E9E, #757575);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        .required {
            color: #f44336;
        }
        .help-text {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>➕ Add New Learning Link</h1>
        
        <form method="POST">
            <div class="form-group">
                <label for="name_resource">Resource Name <span class="required">*</span></label>
                <input type="text" id="name_resource" name="name_resource" required placeholder="e.g., Python Tutorial, JavaScript Course">
                <div class="help-text">Enter a descriptive name for your learning resource</div>
            </div>
            
            <div class="form-group">
                <label for="link">Link <span class="required">*</span></label>
                <input type="url" id="link" name="link" required placeholder="https://example.com/course">
                <div class="help-text">Provide the full URL to the resource</div>
            </div>
            
            <div class="form-group">
                <label for="information">Information</label>
                <textarea id="information" name="information" placeholder="Additional notes, description, or comments about this resource..."></textarea>
                <div class="help-text">Optional: Add any extra details or notes about this resource</div>
            </div>
            
            <div class="button-group">
                <a href="{{ url_for('main') }}" class="btn btn-back">← Back to Main</a>
                <button type="submit" class="btn btn-submit">Save Entry →</button>
            </div>
        </form>
    </div>
</body>
</html>
"""

# Show records template
RECORDS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Links Records</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .stats {
            margin-top: 15px;
            font-size: 1.2em;
        }
        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .btn-primary {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }
        .btn-secondary {
            background: linear-gradient(45deg, #2196F3, #1976D2);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .table-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 20px 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9em;
        }
        td {
            padding: 20px 15px;
            border-bottom: 1px solid #f0f0f0;
            vertical-align: top;
        }
        tr:hover {
            background-color: #f8f9ff;
        }
        tr:last-child td {
            border-bottom: none;
        }
        .link-cell a {
            color: #2196F3;
            text-decoration: none;
            font-weight: 500;
            word-break: break-all;
        }
        .link-cell a:hover {
            text-decoration: underline;
        }
        .timestamp {
            font-size: 0.9em;
            color: #666;
            white-space: nowrap;
        }
        .id-cell {
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            width: 80px;
        }
        .resource-name {
            font-weight: 600;
            color: #333;
            max-width: 200px;
        }
        .information-cell {
            max-width: 300px;
            word-wrap: break-word;
            color: #555;
            line-height: 1.4;
        }
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-size: 1.2em;
        }
        .error {
            background-color: #ffebee;
            color: #c62828;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 5px solid #f44336;
        }
        @media (max-width: 768px) {
            .controls {
                flex-direction: column;
                align-items: stretch;
            }
            .table-container {
                overflow-x: auto;
            }
            table {
                min-width: 800px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 Learning Links Database</h1>
        <div class="stats">
            {% if error %}
                <span>⚠️ Error loading data</span>
            {% else %}
                <span>📊 Total Records: {{ data|length }}</span>
            {% endif %}
        </div>
    </div>
    
    <div class="controls">
        <a href="{{ url_for('main') }}" class="btn btn-secondary">← Back to Main</a>
        <a href="{{ url_for('add_entry') }}" class="btn btn-primary">➕ Add New Entry</a>
    </div>
    
    {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
    {% else %}
        <div class="table-container">
            {% if data %}
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Created At</th>
                            <th>Resource Name</th>
                            <th>Link</th>
                            <th>Information</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in data %}
                            <tr>
                                <td class="id-cell">{{ row.id }}</td>
                                <td class="timestamp">
                                    {% if row.created_at %}
                                        {{ row.created_at[:19].replace('T', ' ') }}
                                    {% else %}
                                        N/A
                                    {% endif %}
                                </td>
                                <td class="resource-name">{{ row.Name_Resource or 'N/A' }}</td>
                                <td class="link-cell">
                                    {% if row.Link %}
                                        <a href="{{ row.Link }}" target="_blank">{{ row.Link }}</a>
                                    {% else %}
                                        N/A
                                    {% endif %}
                                </td>
                                <td class="information-cell">{{ row.Information or 'N/A' }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <div class="no-data">
                    📭 No learning links found in the database.<br>
                    <a href="{{ url_for('add_entry') }}" class="btn btn-primary" style="margin-top: 20px;">Add Your First Entry</a>
                </div>
            {% endif %}
        </div>
    {% endif %}
</body>
</html>
"""

def check_password():
    """Check if user is authenticated"""
    return session.get('authenticated', False)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Password login page (first page)"""
    if check_password():
        return redirect(url_for('main'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == REQUIRED_PASSWORD:
            session['authenticated'] = True
            flash('✅ Access granted! Welcome to Learning Links.', 'success')
            return redirect(url_for('main'))
        else:
            flash('❌ Incorrect password. Please try again.', 'error')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle password authentication"""
    if check_password():
        return redirect(url_for('main'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == REQUIRED_PASSWORD:
            session['authenticated'] = True
            flash('✅ Access granted! Welcome to Learning Links.', 'success')
            return redirect(url_for('main'))
        else:
            flash('❌ Incorrect password. Please try again.', 'error')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/main')
def main():
    """Main page with two buttons (protected)"""
    if not check_password():
        return redirect(url_for('index'))
    return render_template_string(MAIN_TEMPLATE)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.pop('authenticated', None)
    flash('👋 You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    """Add new entry page (protected)"""
    if not check_password():
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Get form data
            name_resource = request.form.get('name_resource', '').strip()
            link = request.form.get('link', '').strip()
            information = request.form.get('information', '').strip()
            
            # Validate required fields
            if not name_resource or not link:
                flash('Resource Name and Link are required fields!', 'error')
                return render_template_string(ADD_ENTRY_TEMPLATE)
            
            # Prepare data for insertion
            data = {
                'Name_Resource': name_resource,
                'Link': link,
                'Information': information if information else None
            }
            response = supabase.table('Important_Learning_Links').insert(data).execute()
            
            if response.data:
                flash(f'✅ Successfully added "{name_resource}" to the database!', 'success')
                return redirect(url_for('main'))
            else:
                flash('❌ Failed to add entry to database. Please try again.', 'error')
                
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
    
    return render_template_string(ADD_ENTRY_TEMPLATE)

@app.route('/records')
def show_records():
    """Show all records page (protected)"""
    if not check_password():
        return redirect(url_for('index'))
    
    try:
        # Fetch data from the Important_Learning_Links table
        response = supabase.table('Important_Learning_Links').select('*').order('created_at', desc=True).execute()
        
        if response.data:
            data = response.data
            error = None
        else:
            data = []
            error = None
            
        return render_template_string(RECORDS_TEMPLATE, data=data, error=error)
        
    except Exception as e:
        error_message = f"Failed to fetch records: {str(e)}"
        return render_template_string(RECORDS_TEMPLATE, data=[], error=error_message)

@app.route('/refresh')
def refresh():
    """Refresh records and redirect to records page (protected)"""
    if not check_password():
        return redirect(url_for('index'))
    return redirect(url_for('show_records'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)