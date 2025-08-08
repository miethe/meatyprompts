import { NextRequest, NextResponse } from 'next/server';

// List of routes that do not require authentication
const PUBLIC_PATHS = ['/login', '/_next', '/favicon.ico', '/api', '/public'];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  // Allow public paths
  if (PUBLIC_PATHS.some((path) => pathname.startsWith(path))) {
    return NextResponse.next();
  }
  // Check for session cookie
  const session = req.cookies.get('session') || req.cookies.get('meatyprompts_session');
  if (!session) {
    const loginUrl = req.nextUrl.clone();
    loginUrl.pathname = '/login';
    loginUrl.search = '';
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next|public|favicon.ico).*)'],
};
