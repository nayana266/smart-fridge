# Smart Fridge Frontend

A Next.js frontend application for AI-powered fridge content analysis, providing inventory insights, carbon impact tracking, and personalized recipe recommendations.

## Features

- **Multi-Image Upload**: Drag & drop interface with progress tracking
- **AI Inventory Detection**: Automatically detects and categorizes food items
- **Carbon Impact Analysis**: Visual badges showing environmental impact
- **Recipe Recommendations**: Personalized recipes based on available ingredients
- **Eco-Friendly Swap Tips**: Suggestions for reducing carbon footprint
- **Mobile Responsive**: Optimized for mobile viewports
- **Demo Mode**: Toggle for testing without real API calls

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **File Upload**: React Dropzone
- **Notifications**: React Hot Toast
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running (see backend documentation)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.local.example .env.local
```

3. Update environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main page component
├── components/            # React components
│   ├── ImageUploader.tsx  # Multi-image upload component
│   ├── InventoryChips.tsx # Inventory management
│   ├── PeopleCountForm.tsx# People count input
│   ├── ResultsPage.tsx    # Analysis results display
│   ├── DemoModeToggle.tsx # Demo mode toggle
│   ├── LoadingSpinner.tsx # Loading indicator
│   └── ErrorMessage.tsx   # Error display
├── lib/                   # Utilities
│   └── api.ts            # API client functions
└── public/               # Static assets
```

## API Integration

The frontend integrates with the backend API for:

- **Presigned Uploads**: Get S3 presigned URLs for direct file uploads
- **Image Analysis**: Send uploaded image keys for AI analysis
- **Health Checks**: Verify API connectivity

### API Endpoints

- `POST /api/presign` - Get presigned upload URL
- `POST /api/analyze` - Analyze uploaded images
- `GET /api/health` - Health check

## Mobile Responsiveness

The application is fully responsive and optimized for mobile devices:

- Touch-friendly drag & drop interface
- Responsive grid layouts
- Mobile-optimized form inputs
- Swipe-friendly navigation
- Optimized image previews

## Demo Mode

Toggle Demo Mode in the header to test the application without requiring:
- Real image uploads
- Backend API connectivity
- S3 configuration

Demo mode uses mock data to showcase all features.

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Code Style

- TypeScript for type safety
- Tailwind CSS for styling
- ESLint for code quality
- Prettier for code formatting

## Deployment

The application can be deployed to any platform that supports Next.js:

- Vercel (recommended)
- Netlify
- AWS Amplify
- Docker containers

### Environment Variables

Required for production:
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.


