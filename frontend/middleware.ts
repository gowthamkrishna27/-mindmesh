import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isLoggedIn = request.cookies.get('mindmesh_logged_in')?.value === 'true';
  const role = request.cookies.get('mindmesh_role')?.value;

  const isPublicRoute =
    pathname === '/signin' ||
    pathname === '/signup' ||
    pathname === '/educator/login' ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/_next') ||
    pathname === '/favicon.ico' ||
    pathname === '/logo.png';

  // 1. Strict Auth: Protect all internal app routes
  if (!isLoggedIn && !isPublicRoute && pathname !== '/') {
    const signInUrl = new URL('/signin', request.url);
    signInUrl.searchParams.set('callbackUrl', pathname);
    if (pathname === '/educator' || pathname.startsWith('/educator')) {
      signInUrl.searchParams.set('role', 'educator');
    }
    return NextResponse.redirect(signInUrl);
  }

  // 2. Prevent logged in users from visiting signin/signup/educator/login
  if (isLoggedIn && (pathname === '/signin' || pathname === '/signup' || pathname === '/educator/login')) {
    return NextResponse.redirect(new URL(role === 'educator' ? '/educator' : '/dashboard', request.url));
  }

  // 3. Strict Role Guard: Non-educators cannot view /educator
  if (isLoggedIn && pathname === '/educator' && role !== 'educator') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|logo.png).*)',
  ],
};
