import { useState, useMemo } from 'react';
import { Search, Users as UsersIcon, Building, Package } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useUsers } from '../hooks/useUsers';
import { UserAssetsModal } from '../components/UserAssetsModal';
import type { User } from '@/types/user';
import { decodeUserData } from '../utils/htmlDecode';

export default function Users() {
  const { data: users = [], isLoading, isError, error } = useUsers();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredUsers = useMemo(() => {
    if (!searchQuery.trim()) return users;
    
    const query = searchQuery.toLowerCase();
    return users.filter(user => {
      const decodedUser = decodeUserData(user);
      return decodedUser.first_name?.toLowerCase().includes(query) ||
             decodedUser.last_name?.toLowerCase().includes(query) ||
             decodedUser.username?.toLowerCase().includes(query) ||
             decodedUser.email?.toLowerCase().includes(query) ||
             decodedUser.department_name?.toLowerCase().includes(query);
    });
  }, [users, searchQuery]);

  const sortedUsers = useMemo(() => {
    return [...filteredUsers].sort((a, b) => {
      // Sort by department first, then by asset count (descending), then by last name
      const deptA = a.department_name || 'ZZZ_Unassigned';
      const deptB = b.department_name || 'ZZZ_Unassigned';
      
      if (deptA !== deptB) {
        return deptA.localeCompare(deptB);
      }
      
      if (a.assets_count !== b.assets_count) {
        return (b.assets_count || 0) - (a.assets_count || 0);
      }
      
      return (a.last_name || '').localeCompare(b.last_name || '');
    });
  }, [filteredUsers]);

  const handleUserClick = (user: User) => {
    setSelectedUser(user);
    setIsModalOpen(true);
  };

  const stats = {
    total: users.length,
    withAssets: users.filter(u => (u.assets_count || 0) > 0).length,
    withDepartment: users.filter(u => u.department_name).length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {isLoading && <p>Loading Users...</p>}
      {isError && <p className='text-red-600'>Error: {error?.message}</p>}
      
      <div className="container mx-auto p-6 space-y-8">
        {/* Header */}
        <header className="space-y-4">
          <div className="flex items-center gap-3">
            <UsersIcon className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                Users Management
              </h1>
              <p className="text-slate-600">
                View users and their assigned assets
              </p>
            </div>
          </div>

          {/* Search */}
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <Input
              type="text"
              placeholder="Search by name, email, or department..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </header>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-l-4 border-l-blue-500">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">Total Users</CardTitle>
              <UsersIcon className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">{stats.total}</div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">Users with Assets</CardTitle>
              <Package className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">{stats.withAssets}</div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-purple-500">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">Assigned to Department</CardTitle>
              <Building className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">{stats.withDepartment}</div>
            </CardContent>
          </Card>
        </div>

        {/* Users Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UsersIcon className="h-5 w-5" />
              Users ({filteredUsers.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 font-medium text-slate-600">Name</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-600">Email</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-600">Department</th>
                    <th className="text-center py-3 px-4 font-medium text-slate-600">Assets</th>
                    <th className="text-center py-3 px-4 font-medium text-slate-600">Licenses</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedUsers.map(user => {
                    const decodedUser = decodeUserData(user);
                    return (
                      <tr 
                        key={user.id} 
                        className="border-b border-slate-100 hover:bg-slate-50 cursor-pointer"
                        onClick={() => handleUserClick(user)}
                      >
                        <td className="py-3 px-4">
                          <div>
                            <div className="font-medium text-slate-900">
                              {decodedUser.first_name} {decodedUser.last_name}
                            </div>
                            <div className="text-sm text-slate-500">
                              @{decodedUser.username}
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-slate-600">
                          {decodedUser.email}
                        </td>
                        <td className="py-3 px-4">
                          {decodedUser.department_name ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {decodedUser.department_name}
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
                              Unassigned
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {user.assets_count ? (
                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-100 text-green-800 text-sm font-medium">
                              {user.assets_count}
                            </span>
                          ) : (
                            <span className="text-slate-400">0</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {user.license_count ? (
                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-purple-100 text-purple-800 text-sm font-medium">
                              {user.license_count}
                            </span>
                          ) : (
                            <span className="text-slate-400">0</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              
              {filteredUsers.length === 0 && !isLoading && (
                <div className="text-center py-8 text-slate-500">
                  No users found matching your search criteria
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* User Assets Modal */}
      <UserAssetsModal
        user={selectedUser}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}