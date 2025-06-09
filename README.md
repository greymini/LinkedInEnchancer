# LinkedIn Enhancer 🚀

A comprehensive AI-powered LinkedIn profile analysis and enhancement tool that helps professionals optimize their profiles, match job opportunities, and advance their careers.


## 🌟 Features

### Core Functionality
- **Real LinkedIn Profile Scraping**: Extract comprehensive profile data using Apify integration
- **AI-Powered Analysis**: Advanced profile analysis using Google Gemini AI
- **Interactive Web Interface**: Clean, modern Streamlit-based UI

### Enhanced Features
- **🎯 Job Fit Analysis**: Compare profiles against job descriptions with detailed match scoring
- **✨ Content Enhancement**: Rewrite profile sections with industry best practices
- **📈 Career Counseling**: Identify skill gaps and get personalized learning recommendations
- **⚡ Quick Actions**: Instant insights with pre-configured analysis options

### Analysis Capabilities
- **Skills Assessment**: Comprehensive skill gap analysis and recommendations
- **Experience Evaluation**: Work history analysis and optimization suggestions
- **Education Alignment**: Educational background assessment
- **Industry Best Practices**: ATS-optimized content suggestions
- **Learning Roadmaps**: Personalized skill development plans with resources

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Google Gemini AI, Agno Agent Framework
- **Data Scraping**: Apify LinkedIn Profile Scraper
- **Backend**: Python 3.11+
- **Data Processing**: Pandas, NumPy
- **Web Requests**: Requests, Beautiful Soup

## 📋 Prerequisites

- Python 3.11 or higher
- Google Gemini API key
- Apify API token (with credits for LinkedIn scraping)
- LinkedIn account (for cookie authentication)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/greymini/LinkedInEnchancer.git
cd LinkedInEnchancer
```

### 2. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
APIFY_API_TOKEN=your_apify_api_token_here
```

### 5. Configure Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your_google_gemini_api_key_here"
APIFY_API_TOKEN = "your_apify_api_token_here"
```

### 6. Run the Application

```bash
python -m streamlit run app.py
```

The application will be available at `http://localhost:8501`

## ⚙️ Detailed Setup Instructions

### Getting Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new project or select existing one
3. Generate an API key
4. Add the key to your environment configuration

### Setting up Apify Integration

1. Create an account at [Apify](https://apify.com/)
2. Add credits to your account ($5-10 recommended)
3. Get your API token from the Apify console
4. Update LinkedIn cookies in `src/services/linkedin_scraper.py`:
   - Log into LinkedIn in your browser
   - Open Developer Tools (F12)
   - Go to Application > Cookies > linkedin.com
   - Copy `li_at` and `JSESSIONID` values
   - Update the `get_working_cookies()` method

### LinkedIn Cookie Setup

For real LinkedIn scraping, you need to update the cookies in the scraper:

```python
# In src/services/linkedin_scraper.py
def get_working_cookies(self) -> List[Dict]:
    return [
        {
            "name": "li_at",
            "value": "YOUR_LI_AT_COOKIE_VALUE",
            "domain": ".linkedin.com"
        },
        {
            "name": "JSESSIONID",
            "value": "YOUR_JSESSIONID_VALUE",
            "domain": ".linkedin.com"
        }
        # ... other cookies
    ]
```

## 📖 Usage Guide

### Basic Profile Analysis

1. **Enter LinkedIn URL**: Paste any LinkedIn profile URL
2. **Click Analyze**: Wait for the scraping and analysis to complete
3. **Review Results**: Get comprehensive profile insights

### Enhanced Features

#### Job Fit Analysis
- Navigate to "Enhanced Features" → "Job Fit Analysis"
- Paste a job description
- Get detailed match scoring and gap analysis

#### Content Enhancement
- Select "Content Enhancement" from enhanced features
- Choose profile section to optimize
- Receive rewritten content with best practices

#### Career Counseling
- Use "Skill Gap Analysis & Career Counseling"
- Specify target role or leave blank for general analysis
- Get personalized learning roadmaps

### Quick Actions

Use the sidebar for instant insights:
- **Profile Strengths**: Identify your key advantages
- **Improvement Areas**: Get specific enhancement suggestions
- **Skill Recommendations**: Discover skills to develop
- **Content Ideas**: Get LinkedIn post suggestions

## 📁 Project Structure

```
LinkedInEnhancer/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .env.example                    # Environment variables template
├── src/
│   ├── agents/                     # AI agent implementations
│   │   ├── base_agent.py          # Base agent class
│   │   ├── profile_analyzer.py    # Profile analysis agent
│   │   ├── job_matcher.py         # Job matching agent
│   │   ├── content_generator.py   # Content enhancement agent
│   │   └── career_counselor.py    # Career counseling agent
│   ├── services/                   # Service layer
│   │   └── linkedin_scraper.py    # LinkedIn scraping service
│   └── ui/                        # User interface
│       └── streamlit_app.py       # Streamlit UI implementation
└── .streamlit/
    └── secrets.toml               # Streamlit secrets (create manually)
```

## 🔧 Configuration Options

### AI Model Settings

You can customize the AI analysis by modifying the agent configurations:

- **Profile Analyzer**: Adjust analysis depth and focus areas
- **Job Matcher**: Configure matching algorithms and scoring weights
- **Content Generator**: Customize tone and style preferences
- **Career Counselor**: Set experience level and industry focus

### Scraping Settings

Modify scraping behavior in `linkedin_scraper.py`:

- **Timeout**: Adjust maximum wait time for scraping
- **Retry Logic**: Configure retry attempts for failed requests
- **Data Extraction**: Customize which profile fields to extract

## 🚨 Important Notes

### Legal and Ethical Usage

- **Respect LinkedIn's Terms of Service**: Only scrape profiles you have permission to access
- **Privacy Compliance**: Follow GDPR, CCPA, and other privacy regulations
- **Rate Limiting**: Don't overwhelm LinkedIn's servers with requests
- **Data Usage**: Use scraped data responsibly and ethically

### Limitations

- **Cookie Expiration**: LinkedIn cookies need periodic renewal
- **Rate Limits**: Apify has usage limits and costs
- **Profile Privacy**: Private profiles cannot be scraped
- **Data Accuracy**: Results depend on profile completeness and accuracy

## 🔍 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

**LinkedIn scraping fails:**
- Check if cookies are expired
- Verify Apify credits are available
- Ensure target profile is public

**AI analysis errors:**
- Verify Google Gemini API key is correct
- Check API quota and usage limits

