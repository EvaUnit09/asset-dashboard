import { Routes, Route } from 'react-router';
import { Layout } from './components/Layout';
import Dashboard from './pages/Dashboard';
import FunQueries from './pages/FunQueries';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/fun-queries" element={<FunQueries />} />
      </Routes>
    </Layout>
  );
}
