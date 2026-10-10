import { AuthScreen } from '@/components/auth-screen';

export const metadata = {
  title: 'Sign In — Mind Mesh',
  description: 'Sign in to access your adaptive learning dependency graph.'
};

export default function SignInPage() {
  return <AuthScreen initialMode="signin" isStandalone />;
}
