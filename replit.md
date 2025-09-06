# Cricket Match Prediction System

## Overview

This is a cricket match prediction system built with React (frontend) and Express.js (backend) that uses machine learning to predict match outcomes. The application allows users to set up match parameters (teams, venues, toss details) and generates comprehensive predictions with win probabilities, expected margins, and detailed analysis factors. The system provides rich visualizations including head-to-head statistics, team strength analysis, venue impact assessments, and key player insights.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript using Vite as the build tool
- **UI Library**: Radix UI components with shadcn/ui design system
- **Styling**: Tailwind CSS with CSS variables for theming support
- **State Management**: TanStack Query (React Query) for server state management
- **Routing**: Wouter for lightweight client-side routing
- **Charts**: Recharts for data visualization
- **Form Handling**: React Hook Form with Zod validation

### Backend Architecture
- **Runtime**: Node.js with Express.js framework
- **Language**: TypeScript with ES modules
- **API Design**: RESTful API with comprehensive error handling and request logging
- **Data Validation**: Zod schemas for type-safe data validation
- **Development**: Hot reloading with tsx and Vite middleware integration

### Data Storage Solutions
- **Database**: PostgreSQL with Drizzle ORM for type-safe database operations
- **Connection**: Neon Database serverless PostgreSQL
- **Schema Management**: Drizzle Kit for migrations and schema management
- **In-Memory Storage**: Fallback MemStorage implementation for development/testing
- **Session Storage**: PostgreSQL-based session storage with connect-pg-simple

### Database Schema Design
- **Teams**: Store team information (name, colors, logos)
- **Venues**: Cricket ground details with statistical data (capacity, average scores, boundary percentages)
- **Matches**: Match records linking teams and venues with results
- **Predictions**: ML-generated predictions with probability scores and explanatory factors
- **Statistics Tables**: Head-to-head stats, team performance metrics, and venue-specific team performance

### Machine Learning Integration
- **Service Layer**: MLService class designed to interface with Python ML models
- **Prediction Factors**: Venue advantage, toss impact, recent form, and head-to-head records
- **Mock Implementation**: Currently uses algorithmic approximations with plans for Python subprocess integration
- **Probability Calculation**: Sophisticated multi-factor analysis for win probability generation

### Authentication and Authorization
- **Session Management**: Express sessions with PostgreSQL storage
- **Security Headers**: Basic security middleware for API protection
- **CORS Configuration**: Development-friendly CORS setup

### Component Architecture
- **Modular Design**: Reusable UI components for match setup, predictions, and analysis
- **Data Visualization**: Specialized components for charts, statistics, and probability displays
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Loading States**: Comprehensive loading and error state management

## External Dependencies

### Core Framework Dependencies
- **React Ecosystem**: React 18, React DOM, TanStack Query for state management
- **Backend Framework**: Express.js with TypeScript support
- **Database**: Drizzle ORM with Neon Database PostgreSQL connection
- **Validation**: Zod for runtime type checking and validation

### UI and Design System
- **Component Library**: Radix UI primitives for accessible components
- **Styling**: Tailwind CSS with PostCSS processing
- **Icons**: Lucide React icon library
- **Charts**: Recharts for data visualization
- **Carousel**: Embla Carousel for interactive components

### Development and Build Tools
- **Build System**: Vite for fast development and optimized production builds
- **TypeScript**: Full TypeScript support across frontend and backend
- **Development Server**: Vite dev server with HMR and Express middleware integration
- **Linting**: ESBuild for production builds

### Database and Storage
- **Database Provider**: Neon Database serverless PostgreSQL
- **ORM**: Drizzle ORM with PostgreSQL dialect
- **Session Store**: connect-pg-simple for PostgreSQL session management
- **Migration Tools**: Drizzle Kit for schema migrations

### Utility Libraries
- **Date Handling**: date-fns for date manipulation
- **Routing**: Wouter for lightweight client-side routing
- **Class Management**: clsx and tailwind-merge for conditional styling
- **Form Management**: React Hook Form with Hookform Resolvers

### Replit-Specific Integrations
- **Development Tools**: Replit-specific Vite plugins for error handling and cartography
- **Runtime Error Handling**: Custom error modal overlay for development
- **Environment Detection**: Replit environment-aware configuration