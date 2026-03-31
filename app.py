from flask import Flask, render_template, jsonify, request
from data.database import get_all_jobs, search_jobs, get_job_statistics
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Main job board page"""
    return render_template('index.html')

@app.route('/api/jobs')
def api_jobs():
    """API endpoint to get all jobs"""
    try:
        jobs = get_all_jobs()
        # Convert tuple to dict for JSON serialization
        jobs_data = []
        for job in jobs:
            job_dict = {
                'id': job[0],
                'url': job[1],
                'source': job[2],
                'title': job[3],
                'company': job[4],
                'description': job[5][:500] + '...' if len(job[5]) > 500 else job[5],  # Truncate description
                'location': job[6],
                'city': job[7],
                'state': job[8],
                'country': job[9],
                'seniority_level': job[11],
                'employment_type': job[12],
                'salary_min': job[14],
                'salary_max': job[15],
                'salary_avg': job[16],
                'date_posted': job[25]
            }
            jobs_data.append(job_dict)
        
        return jsonify({
            'success': True,
            'jobs': jobs_data,
            'total': len(jobs_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jobs/search')
def api_search_jobs():
    """API endpoint to search jobs"""
    try:
        title = request.args.get('title', '')
        location = request.args.get('location', '')
        num_jobs = int(request.args.get('limit', 50))
        
        jobs = search_jobs(title=title, location=location, num_jobs=num_jobs)
        
        # Convert tuple to dict for JSON serialization
        jobs_data = []
        for job in jobs:
            job_dict = {
                'id': job[0],
                'url': job[1],
                'source': job[2],
                'title': job[3],
                'company': job[4],
                'description': job[5][:500] + '...' if len(job[5]) > 500 else job[5],
                'location': job[6],
                'city': job[7],
                'state': job[8],
                'country': job[9],
                'seniority_level': job[11],
                'employment_type': job[12],
                'salary_min': job[14],
                'salary_max': job[15],
                'salary_avg': job[16],
                'date_posted': job[25]
            }
            jobs_data.append(job_dict)
        
        return jsonify({
            'success': True,
            'jobs': jobs_data,
            'total': len(jobs_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint to get job statistics"""
    try:
        stats = get_job_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """API endpoint to handle resume file uploads"""
    try:
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['resume']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': 'Only PDF files are allowed'
            }), 400
        
        # Validate file size (10MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            return jsonify({
                'success': False,
                'error': 'File size must be less than 10MB'
            }), 400
        
        # Generate unique filename
        from werkzeug.utils import secure_filename
        import uuid
        from datetime import datetime
        
        # Create safe filename
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{unique_id}_{original_filename}"
        
        # Save file to uploads directory
        upload_path = os.path.join('uploads', filename)
        file.save(upload_path)
        
        # TODO: Store resume metadata in database
        # TODO: Extract text from PDF
        # TODO: Calculate job matches
        
        return jsonify({
            'success': True,
            'message': f'Resume uploaded successfully as {filename}',
            'filename': filename,
            'file_size': file_size
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
