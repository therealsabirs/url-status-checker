from flask import Flask, request, render_template, redirect, url_for, send_file
import requests
import io
import csv

app = Flask(__name__)

# Store results in global dict — use Redis, DB, or Flask-Caching for production
global_results = {}

@app.route('/', methods=['GET', 'POST'])
def check_urls():
    global global_results
    results = {}
    if request.method == 'POST':
        urls_text = request.form.get('urls', '')
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        for url in urls:
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                final_url = response.url
                results[url] = f"{response.status_code} → {final_url}" if final_url != url else str(response.status_code)
            except requests.exceptions.RequestException as e:
                results[url] = f"Error: {str(e)}"
        global_results = results  # Store globally
    return render_template('index.html', results=global_results)


@app.route('/export')
def export_csv():
    global global_results
    if not global_results:
        return redirect(url_for('check_urls'))

    csv_io = io.StringIO()
    writer = csv.writer(csv_io)
    writer.writerow(['URL', 'Status'])
    for url, status in global_results.items():
        writer.writerow([url, status])

    csv_io.seek(0)
    return send_file(
        io.BytesIO(csv_io.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='url_status_results.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
