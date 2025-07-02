# LinkedIn MCP Frontend

> **Quick Start: One Command for Everything!**
>
> To start the backend, API bridge, and this dashboard all at once, just run:
> ```bat
> start_all.bat
> ```
> This will open the dashboard in your browser and start all services in separate terminals.

A beautiful React frontend for the LinkedIn MCP Server that provides an intuitive user interface for LinkedIn automation.

## Features

- 🎨 **Modern UI**: Clean, responsive design with Tailwind CSS
- 🔐 **Secure Login**: Environment-based authentication
- 🔍 **Profile Search**: Search and view LinkedIn profiles
- 📱 **Feed Browser**: Browse and interact with LinkedIn feed
- 💬 **Post Interactions**: Like, comment, and read posts
- ⚙️ **Settings Management**: Configure server settings
- 📊 **Real-time Status**: Monitor server connection status

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start the Development Server

```bash
npm start
```

The React app will start on `http://localhost:3000`

### 3. Start the API Bridge

In a separate terminal, start the API bridge:

```bash
python api_bridge.py
```

The API bridge will run on `http://localhost:8000`

## Project Structure

```
src/
├── components/          # React components
│   ├── Dashboard.js     # Main dashboard
│   ├── Login.js         # LinkedIn login
│   ├── ProfileSearch.js # Profile search interface
│   ├── FeedBrowser.js   # Feed browsing
│   ├── PostInteraction.js # Post interactions
│   ├── SettingsPage.js  # Settings and configuration
│   └── Sidebar.js       # Navigation sidebar
├── App.js              # Main app component
├── index.js            # App entry point
└── index.css           # Global styles with Tailwind
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Technologies Used

- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP client
- **React Router** - Navigation

## API Endpoints

The frontend communicates with the API bridge on the following endpoints:

- `GET /api/health` - Health check
- `POST /api/login_linkedin_secure` - LinkedIn login
- `POST /api/search_linkedin_profiles` - Search profiles
- `POST /api/browse_linkedin_feed` - Browse feed
- `POST /api/interact_with_linkedin_post` - Interact with posts
- `POST /api/view_linkedin_profile` - View profile

## Configuration

The frontend is configured to proxy requests to `http://localhost:8000` (the API bridge) during development.

## Security

- Credentials are never exposed in the frontend
- All sensitive data is handled server-side
- CORS is properly configured for development
- Environment variables are used for configuration

## Development

### Adding New Features

1. Create new components in `src/components/`
2. Add routes in `src/App.js`
3. Update the sidebar navigation in `src/components/Sidebar.js`
4. Add API endpoints in `api_bridge.py`

### Styling

The project uses Tailwind CSS for styling. Custom styles can be added in `src/index.css` or by extending the Tailwind configuration in `tailwind.config.js`.

## Production Build

To build for production:

```bash
npm run build
```

This creates an optimized build in the `build/` directory.

## Troubleshooting

### Common Issues

1. **Port 3000 already in use**: Change the port in `package.json` or kill the existing process
2. **API connection failed**: Ensure the API bridge is running on port 8000
3. **CORS errors**: Check that the API bridge CORS settings include `http://localhost:3000`

### Development Tips

- Use React Developer Tools for debugging
- Check the browser console for errors
- Monitor the API bridge logs for server-side issues
- Use the Network tab to debug API requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see the main project LICENSE file for details. 