import { AuthScreen } from '@/components/auth-screen';

export const metadata = {
  title: 'Educator Sign In — Mind Mesh',
  description: 'Sign in to access your educator dashboard and cohort heatmap.'
};

export default function EducatorLoginPage() {
  return <AuthScreen initialMode="signin" initialRole="educator" isStandalone />;
}
