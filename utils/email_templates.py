from typing import List, Dict

def create_job_email_content(jobs: List[Dict]) -> str:
    """Create HTML email content with job listings"""
    
    html_content = """
    <html>
    <head>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background-color: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                border-bottom: 2px solid #3498db;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }
            .job { 
                border: 1px solid #ddd; 
                margin: 15px 0; 
                padding: 20px; 
                border-radius: 8px;
                background-color: #fafafa;
                transition: box-shadow 0.3s ease;
            }
            .job:hover {
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .title { 
                color: #2c3e50; 
                font-size: 20px; 
                font-weight: bold; 
                margin-bottom: 8px;
                text-decoration: none;
            }
            .company { 
                color: #7f8c8d; 
                font-size: 16px; 
                margin-bottom: 8px;
                font-weight: 500;
            }
            .location { 
                color: #7f8c8d; 
                font-size: 14px; 
                margin-bottom: 12px;
            }
            .salary { 
                color: #27ae60; 
                font-weight: bold; 
                margin-bottom: 12px;
                font-size: 14px;
            }
            .description { 
                color: #34495e; 
                line-height: 1.6; 
                margin-bottom: 15px;
                font-size: 14px;
            }
            .skills { 
                color: #3498db; 
                font-size: 13px;
                margin-bottom: 15px;
            }
            .apply-link { 
                background-color: #3498db; 
                color: white; 
                padding: 10px 20px; 
                text-decoration: none; 
                border-radius: 5px; 
                display: inline-block; 
                margin-top: 10px;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }
            .apply-link:hover {
                background-color: #2980b9;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #7f8c8d;
                font-size: 12px;
            }
            .job-count {
                background-color: #3498db;
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 12px;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Job Search Results</h1>
                <p>Here are the job listings you requested:</p>
                <span class="job-count">{count} jobs found</span>
            </div>
    """.format(count=len(jobs))
    
    for i, job in enumerate(jobs, 1):
        # Format salary display
        salary_display = ""
        if job.get('salary_raw'):
            salary_display = f"💰 {job.get('salary_raw')}"
        elif job.get('salary_min') and job.get('salary_max'):
            salary_display = f"💰 ${job.get('salary_min'):,} - ${job.get('salary_max'):,}"
        elif job.get('salary_min'):
            salary_display = f"💰 ${job.get('salary_min'):,}+"
        else:
            salary_display = "💰 Salary not specified"
        
        # Format skills display
        skills = job.get('skills', [])
        if isinstance(skills, str):
            # If skills is a JSON string, try to parse it
            try:
                import json
                skills = json.loads(skills)
            except:
                skills = [skills] if skills else []
        
        skills_display = ""
        if skills:
            if isinstance(skills, list):
                skills_display = f"🔧 Skills: {', '.join(skills[:5])}"  # Show first 5 skills
                if len(skills) > 5:
                    skills_display += f" (+{len(skills)-5} more)"
            else:
                skills_display = f"🔧 Skills: {skills}"
        else:
            skills_display = "🔧 Skills: Not specified"
        
        # Format experience display
        experience_display = ""
        if job.get('yoe_raw'):
            experience_display = f"📈 {job.get('yoe_raw')}"
        elif job.get('yoe_min') and job.get('yoe_max'):
            experience_display = f"📈 {job.get('yoe_min')}-{job.get('yoe_max')} years"
        elif job.get('yoe_min'):
            experience_display = f"📈 {job.get('yoe_min')}+ years"
        else:
            experience_display = "📈 Experience: Not specified"
        
        # Format employment type
        employment_type = job.get('employment_type', 'Not specified')
        if employment_type and employment_type.lower() != 'none':
            employment_type_display = f"📋 {employment_type}"
        else:
            employment_type_display = "📋 Employment type: Not specified"
        
        html_content += f"""
            <div class="job">
                <div class="title">{i}. {job.get('title', 'Unknown Title')}</div>
                <div class="company">🏢 {job.get('company_name', 'Unknown Company')}</div>
                <div class="location">📍 {job.get('location', 'Unknown Location')}</div>
                <div class="salary">{salary_display}</div>
                <div class="location">{experience_display}</div>
                <div class="location">{employment_type_display}</div>
                <div class="description">{job.get('description', 'No description available')[:300]}...</div>
                <div class="skills">{skills_display}</div>
                <a href="{job.get('job_url', '#')}" class="apply-link" target="_blank">View Job & Apply</a>
            </div>
        """
    
    html_content += """
            <div class="footer">
                <p><em>Job search results generated by Job Insights Agent</em></p>
                <p>💡 Tip: Click "View Job & Apply" to see the full job posting and apply directly</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def create_simple_job_email_content(jobs: List[Dict]) -> str:
    """Create a simpler text-based email content"""
    
    content = f"Job Search Results - {len(jobs)} jobs found\n\n"
    content += "=" * 50 + "\n\n"
    
    for i, job in enumerate(jobs, 1):
        content += f"{i}. {job.get('title', 'Unknown Title')}\n"
        content += f"   Company: {job.get('company_name', 'Unknown Company')}\n"
        content += f"   Location: {job.get('location', 'Unknown Location')}\n"
        content += f"   Salary: {job.get('salary_raw', 'Not specified')}\n"
        content += f"   URL: {job.get('job_url', 'Not available')}\n"
        content += f"   Description: {job.get('description', 'No description')[:200]}...\n"
        content += "\n" + "-" * 40 + "\n\n"
    
    content += "\nGenerated by Job Insights Agent"
    return content
