# 🌿 AgriNova - Smart Farming Assistant with Backend

A complete, full-stack web application with Flask backend serving all farming features in one unified platform.

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Server**: Python Flask Web Server
- **Port**: 5000
- **Database**: localStorage (client) + Python sessions (server)

## 📋 Project Overview

AgriNova is an AI-powered farming assistant that provides:
- **Crop Advisory**: Get crop recommendations based on your farm conditions
- **Fertilizer Guidance**: Find the right nutrient balance for your crops
- **AI Chatbot**: Get instant farming advice 24/7
- **Support System**: Submit queries and get expert assistance

---

## ⚡ Quick Start (5 Minutes)

### Run on Windows:
```powershell
cd "c:\Users\nihal\Downloads\Project\AgriNova_OneSite"
.\setup.ps1
```

Or simply:
```cmd
setup.bat
```

Then open browser: **http://localhost:5000**

---

```
AgriNova_OneSite/
├── index.html                    # Landing page (public)
├── login.html                    # Login page
├── signup.html                   # Registration page
├── forgotpassword.html          # Password reset
├── home.html                     # Dashboard (protected)
├── crop-advisory.html           # Crop recommendations
├── fertilizer.html              # Fertilizer guidance
├── chatbot.html                 # AI assistant
├── support.html                 # Support tickets
├── styles.css                   # Complete styling (600+ lines)
├── script.js                    # All functionality (400+ lines)
├── README.md                    # This file
└── assets/
    └── farmer.svg               # Hero illustration
```

## 🚀 Quick Start

### 1. Open the Application
Simply open `index.html` in any modern web browser (Chrome, Firefox, Edge, Safari).

```
File → Open → Select index.html
```

### 2. Navigate the Site
- **Landing Page**: Shows features and statistics
- **Sign Up**: Create a new account
- **Login**: Access with email and password
- **Dashboard**: View all available services
- **Services**: Access crop advisory, fertilizer, chatbot, support

## 👤 User Workflow

### First Time User
1. Open `index.html`
2. Click "Sign Up Free" button
3. Fill in: Name, Email, Mobile, Password
4. Click "Sign Up"
5. Redirected to Login page
6. Enter your credentials
7. Access Dashboard

### Existing User
1. Open `index.html`
2. Click "Login" button
3. Enter email and password
4. Access Dashboard with all services

## 🌱 Features Explained

### Crop Advisory
**Purpose**: Get crop recommendations based on farm conditions

**How to Use**:
1. From Dashboard, click "Get Advice"
2. Enter your farm details:
   - State (UP, Punjab, MP, etc.)
   - Soil Type (Loamy, Black, Sandy, Clay, Red)
   - Season (Kharif, Rabi, Zaid)
   - Water Availability (Low, Medium, High)
   - Temperature (in °C)
3. Click "Get Recommendation"
4. View recommended crop with explanation

### Fertilizer Recommendation
**Purpose**: Get fertilizer suggestions based on soil conditions

**How to Use**:
1. From Dashboard, click "Get Recommendation"
2. Enter soil details:
   - Crop type (Wheat, Rice, Maize, Cotton, Sugarcane)
   - Nitrogen value (kg/ha)
   - Phosphorus value (kg/ha)
   - Potassium value (kg/ha)
   - Soil pH
   - Preference (Chemical, Organic, Both)
3. Click "Get Fertilizer Recommendation"
4. View recommended fertilizer amounts

### AI Chatbot
**Purpose**: Get instant answers to farming questions

**How to Use**:
1. From Dashboard, click "Chat Now"
2. Type your question about:
   - Fertilizer and nutrients
   - Crop diseases and management
   - Weather patterns and planning
   - Crop selection
   - Water management
   - Soil health
3. Press Send
4. Get instant AI response

**Example Questions**:
- "What fertilizer should I use?"
- "How do I prevent crop diseases?"
- "What should I plant in Rabi season?"
- "How much water does rice need?"

### Support System
**Purpose**: Submit problems and get expert support

**How to Use**:
1. From Dashboard, click "Get Support"
2. Fill in:
   - Your Name
   - Phone Number
   - Problem/Query (describe in detail)
3. Click "Submit Request"
4. Get confirmation
5. Support team will contact you via email or phone

## 🔐 Security & Data

### Authentication
- **Login Protection**: Protected pages redirect to login if not authenticated
- **Session Management**: Uses browser localStorage for session persistence
- **Data Storage**: All user data stored locally (no server needed)

### User Data Stored
- User name
- Email address
- Mobile number
- Password (stored in localStorage)
- Support requests history
- Language preference

### Reset Data
To clear all stored data:
1. Open browser console (F12)
2. Run: `localStorage.clear()`
3. Refresh page

## 🎨 Design Features

### Responsive Design
- Desktop: Full layout with multiple columns
- Tablet (768px): Optimized grid layout
- Mobile (480px): Single column with hamburger menu

### Color Scheme
- Primary Green: #2e7d32 (farming/nature)
- Light Green: #1b5e20 (darker accent)
- Background: #eef7ea (soft green)
- Text: #333 (dark gray)

### Mobile Features
- Hamburger menu toggle
- Touch-friendly buttons
- Optimized form inputs
- Readable text sizes

## 🌐 Language Support

The site supports multiple languages:
- **English** (Default)
- **Hindi** (हिन्दी)

**To Change Language**:
1. Go to Dashboard (home.html)
2. Use language selector (top-right)
3. Page content updates automatically

## 📱 Browser Compatibility

Works on:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 🛠️ Technologies Used

### Frontend
- HTML5 (Semantic markup)
- CSS3 (Grid, Flexbox, Responsive)
- Vanilla JavaScript (No dependencies)

### Storage
- Browser localStorage (Client-side only)
- No backend server required
- No database needed

### Assets
- SVG graphics (Farmer illustration)
- Unicode emojis (Icons)

## 📖 File Descriptions

### index.html (Landing Page)
- Public page with features overview
- Login/Signup buttons
- Statistics and call-to-action
- Responsive design

### login.html
- Email and password input
- Form validation
- Links to signup and forgot password
- Green gradient background

### signup.html
- Name, email, mobile, password fields
- Form validation
- Link to login page
- Stores user data in localStorage

### forgotpassword.html
- Email verification
- New password input
- Password confirmation
- Updates password in localStorage

### home.html (Dashboard)
- Navigation menu
- Language switcher
- User profile display
- 4 service cards
- Logout button

### crop-advisory.html
- State selection dropdown
- Soil type selector
- Season selection
- Water availability
- Temperature input
- Real-time recommendations
- Beautiful result display

### fertilizer.html
- Crop selection
- NPK input fields
- Soil pH input
- Organic/chemical preference
- Detailed fertilizer suggestions
- Soil health advice

### chatbot.html
- Chat message display
- User input field
- AI response system
- Keywords-based replies
- Farming knowledge base

### support.html
- Contact form
- Query submission
- Support contact information
- Business hours display
- Confirmation message

### styles.css
- **Lines**: 600+
- **Sections**: 
  - Global resets and typography
  - Auth page styling
  - Header and navigation
  - Forms and inputs
  - Cards and layouts
  - Chat interface
  - Footer
  - Mobile responsiveness

### script.js
- **Lines**: 400+
- **Functions**:
  - Mobile menu toggle
  - Language switching
  - Login/Signup handling
  - Crop recommendation logic
  - Fertilizer calculation
  - Chatbot responses
  - Support form submission
  - Page protection
  - Data persistence

## 🔧 Customization

### Change Colors
Edit `styles.css`:
```css
/* Primary green */
#2e7d32

/* Dark green accent */
#1b5e20

/* Light background */
#eef7ea
```

### Add New Crops
Edit `script.js` in `getCropRecommendation()` function

### Add Chatbot Responses
Edit `script.js` in `getChatbotReply()` function

### Modify Fertilizer Logic
Edit `script.js` in `getFertilizerRecommendation()` function

## 📝 Default Test Credentials

For testing purposes:
- **Email**: farmer@agrinova.com
- **Password**: password123

**To Create Test Account**:
1. Click Sign Up
2. Fill form with any details
3. Click Sign Up
4. Use those credentials to login

## 🐛 Troubleshooting

### "Page keeps redirecting to login"
- Check if you're logged in
- Try: Logout → Sign Up → Login

### "Form not submitting"
- Check browser console (F12) for errors
- Ensure all fields are filled
- Try refreshing page

### "Data not saving"
- Ensure localStorage is enabled
- Not in private/incognito mode
- Check browser storage quota

### "Mobile menu not working"
- Ensure JavaScript is enabled
- Try refreshing page
- Check browser compatibility

## 📞 Support & Contact

For issues or suggestions:
- **Email**: agrinova@gmail.com
- **Phone**: +91 4179435611
- **Hours**: 24/7 Available

## 📄 License

AgriNova - Smart Farming Assistant
© 2026 All Rights Reserved

## 🌟 Features Roadmap

Future enhancements:
- Real-time weather integration
- Disease identification with image upload
- Market price tracking
- Weather alerts
- Peer community forum
- Expert consultation booking
- Mobile app version

## 🙏 Acknowledgments

Built with dedication to help farmers achieve better yields through smart decisions and expert guidance.

---

**Last Updated**: 2026
**Version**: 1.0
**Status**: Complete and Production Ready
