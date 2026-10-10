import { AuthScreen } from '@/components/auth-screen';

export const metadata = {
  title: 'Sign Up — Mind Mesh',
  description: 'Create an account to begin adaptive learning diagnostics in DBMS.'
};

export default function SignUpPage() {
  return <AuthScreen initialMode="signup" isStandalone />;
}
