import { Routes, Route } from 'react-router';
import { Layout } from './components/Layout';
import Dashboard from './pages/Dashboard';
import FunQueries from './pages/FunQueries';
import Users from './pages/Users';
import Assets from './pages/Assets';
import AssetEdit from './pages/AssetEdit';


export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/fun-queries" element={<FunQueries />} />
        <Route path="/users" element={<Users />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/assets/:id/edit" element={<AssetEdit />} />
      </Routes>
    </Layout>
  );
}
