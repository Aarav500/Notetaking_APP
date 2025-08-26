import React, { useState } from 'react';
import { 
  Users, Flag, Rss, ArrowLeft, Search, MoreHorizontal, 
  UserPlus, Trash, Ban, CheckCircle, RefreshCw, Plus, X, Check
} from 'lucide-react';
import { Button } from '../ui/button';

// Mock data for users
const MOCK_USERS = [
  { id: 1, name: 'Aarav', email: 'aarav@example.com', role: 'admin', status: 'active', lastActive: '2025-07-30T10:30:00Z' },
  { id: 2, name: 'Sophia', email: 'sophia@example.com', role: 'user', status: 'active', lastActive: '2025-07-29T15:45:00Z' },
  { id: 3, name: 'Liam', email: 'liam@example.com', role: 'user', status: 'active', lastActive: '2025-07-28T09:20:00Z' },
  { id: 4, name: 'Emma', email: 'emma@example.com', role: 'user', status: 'inactive', lastActive: '2025-07-15T11:10:00Z' },
  { id: 5, name: 'Noah', email: 'noah@example.com', role: 'user', status: 'suspended', lastActive: '2025-07-10T14:30:00Z' },
];

// Mock data for flagged content
const MOCK_FLAGGED_CONTENT = [
  { 
    id: 1, 
    type: 'note', 
    title: 'Potentially harmful content', 
    content: 'This note contains potentially harmful instructions...',
    reportedBy: 'Sophia',
    reportedAt: '2025-07-28T14:30:00Z',
    status: 'pending'
  },
  { 
    id: 2, 
    type: 'comment', 
    title: 'Inappropriate language', 
    content: 'This comment contains inappropriate language...',
    reportedBy: 'Liam',
    reportedAt: '2025-07-27T09:15:00Z',
    status: 'pending'
  },
  { 
    id: 3, 
    type: 'note', 
    title: 'Copyright violation', 
    content: 'This note may contain copyrighted material...',
    reportedBy: 'Emma',
    reportedAt: '2025-07-26T16:45:00Z',
    status: 'resolved'
  },
];

// Mock data for feeds
const MOCK_FEEDS = [
  { 
    id: 1, 
    name: 'ArXiv ML Papers', 
    source: 'arxiv',
    category: 'cs.LG',
    lastSync: '2025-07-30T08:30:00Z',
    status: 'active',
    itemCount: 156
  },
  { 
    id: 2, 
    name: 'Stanford NLP YouTube', 
    source: 'youtube',
    channel: 'stanfordnlp',
    lastSync: '2025-07-29T10:15:00Z',
    status: 'active',
    itemCount: 42
  },
  { 
    id: 3, 
    name: 'MIT AI Blog', 
    source: 'rss',
    url: 'https://ai.mit.edu/feed',
    lastSync: '2025-07-28T14:45:00Z',
    status: 'error',
    itemCount: 78
  },
];

const AdminPanel = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState(MOCK_USERS);
  const [flaggedContent, setFlaggedContent] = useState(MOCK_FLAGGED_CONTENT);
  const [feeds, setFeeds] = useState(MOCK_FEEDS);
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddingUser, setIsAddingUser] = useState(false);
  const [newUser, setNewUser] = useState({ name: '', email: '', role: 'user' });
  const [isAddingFeed, setIsAddingFeed] = useState(false);
  const [newFeed, setNewFeed] = useState({ name: '', source: 'arxiv', category: '', url: '', channel: '' });
  const [isSyncingFeeds, setIsSyncingFeeds] = useState(false);
  
  // Filter users based on search term
  const filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Filter flagged content based on search term
  const filteredFlaggedContent = flaggedContent.filter(item => 
    item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.reportedBy.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Filter feeds based on search term
  const filteredFeeds = feeds.filter(feed => 
    feed.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    feed.source.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Handle user actions
  const handleAddUser = () => {
    if (!newUser.name || !newUser.email) return;
    
    const user = {
      id: Date.now(),
      name: newUser.name,
      email: newUser.email,
      role: newUser.role,
      status: 'active',
      lastActive: new Date().toISOString()
    };
    
    setUsers([...users, user]);
    setNewUser({ name: '', email: '', role: 'user' });
    setIsAddingUser(false);
  };
  
  const handleDeleteUser = (userId) => {
    setUsers(users.filter(user => user.id !== userId));
  };
  
  const handleSuspendUser = (userId) => {
    setUsers(users.map(user => 
      user.id === userId ? { ...user, status: 'suspended' } : user
    ));
  };
  
  const handleActivateUser = (userId) => {
    setUsers(users.map(user => 
      user.id === userId ? { ...user, status: 'active' } : user
    ));
  };
  
  // Handle flagged content actions
  const handleResolveFlaggedContent = (contentId) => {
    setFlaggedContent(flaggedContent.map(item => 
      item.id === contentId ? { ...item, status: 'resolved' } : item
    ));
  };
  
  const handleDeleteFlaggedContent = (contentId) => {
    setFlaggedContent(flaggedContent.filter(item => item.id !== contentId));
  };
  
  // Handle feed actions
  const handleAddFeed = () => {
    if (!newFeed.name) return;
    
    const feed = {
      id: Date.now(),
      name: newFeed.name,
      source: newFeed.source,
      category: newFeed.category,
      url: newFeed.url,
      channel: newFeed.channel,
      lastSync: new Date().toISOString(),
      status: 'active',
      itemCount: 0
    };
    
    setFeeds([...feeds, feed]);
    setNewFeed({ name: '', source: 'arxiv', category: '', url: '', channel: '' });
    setIsAddingFeed(false);
  };
  
  const handleDeleteFeed = (feedId) => {
    setFeeds(feeds.filter(feed => feed.id !== feedId));
  };
  
  const handleSyncFeeds = async () => {
    setIsSyncingFeeds(true);
    
    try {
      // In a real implementation, this would be an API call
      // await api.post('/admin/sync-feeds');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update last sync time
      setFeeds(feeds.map(feed => ({
        ...feed,
        lastSync: new Date().toISOString(),
        status: Math.random() > 0.1 ? 'active' : 'error' // Simulate some errors
      })));
    } catch (error) {
      console.error('Error syncing feeds:', error);
    } finally {
      setIsSyncingFeeds(false);
    }
  };
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    });
  };
  
  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'suspended':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'resolved':
        return 'bg-blue-100 text-blue-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Render users tab
  const renderUsersTab = () => (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="relative w-64">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search users..."
            className="pl-8 pr-4 py-2 w-full rounded-md border border-input bg-background"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <Button onClick={() => setIsAddingUser(true)}>
          <UserPlus className="h-4 w-4 mr-1" />
          Add User
        </Button>
      </div>
      
      {isAddingUser && (
        <div className="mb-4 p-4 border rounded-md bg-muted/20">
          <h3 className="font-medium mb-3">Add New User</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-1">Name</label>
              <input
                type="text"
                id="name"
                value={newUser.name}
                onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                id="email"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="role" className="block text-sm font-medium mb-1">Role</label>
              <select
                id="role"
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" size="sm" onClick={() => setIsAddingUser(false)}>
              <X className="h-4 w-4 mr-1" />
              Cancel
            </Button>
            <Button size="sm" onClick={handleAddUser}>
              <Check className="h-4 w-4 mr-1" />
              Add User
            </Button>
          </div>
        </div>
      )}
      
      <div className="border rounded-md overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium">Name</th>
              <th className="px-4 py-2 text-left text-sm font-medium">Email</th>
              <th className="px-4 py-2 text-left text-sm font-medium">Role</th>
              <th className="px-4 py-2 text-left text-sm font-medium">Status</th>
              <th className="px-4 py-2 text-left text-sm font-medium">Last Active</th>
              <th className="px-4 py-2 text-right text-sm font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredUsers.map(user => (
              <tr key={user.id} className="hover:bg-muted/20">
                <td className="px-4 py-3">{user.name}</td>
                <td className="px-4 py-3">{user.email}</td>
                <td className="px-4 py-3 capitalize">{user.role}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadgeClass(user.status)}`}>
                    {user.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{formatDate(user.lastActive)}</td>
                <td className="px-4 py-3 text-right">
                  <div className="relative group inline-block">
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                    <div className="absolute right-0 mt-1 w-40 bg-background border rounded-md shadow-md hidden group-hover:block z-10">
                      {user.status === 'active' ? (
                        <button 
                          className="w-full text-left px-3 py-2 text-sm hover:bg-muted text-red-600"
                          onClick={() => handleSuspendUser(user.id)}
                        >
                          <Ban className="h-4 w-4 inline mr-1" />
                          Suspend
                        </button>
                      ) : (
                        <button 
                          className="w-full text-left px-3 py-2 text-sm hover:bg-muted text-green-600"
                          onClick={() => handleActivateUser(user.id)}
                        >
                          <CheckCircle className="h-4 w-4 inline mr-1" />
                          Activate
                        </button>
                      )}
                      <button 
                        className="w-full text-left px-3 py-2 text-sm hover:bg-muted text-red-600"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        <Trash className="h-4 w-4 inline mr-1" />
                        Delete
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredUsers.length === 0 && (
          <div className="p-4 text-center text-muted-foreground">
            No users found.
          </div>
        )}
      </div>
    </div>
  );
  
  // Render flagged content tab
  const renderFlaggedContentTab = () => (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="relative w-64">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search flagged content..."
            className="pl-8 pr-4 py-2 w-full rounded-md border border-input bg-background"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      
      <div className="space-y-4">
        {filteredFlaggedContent.map(item => (
          <div key={item.id} className="border rounded-md p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-medium">{item.title}</h3>
                <div className="flex items-center text-sm text-muted-foreground mt-1">
                  <span className="capitalize">{item.type}</span>
                  <span className="mx-2">•</span>
                  <span>Reported by {item.reportedBy}</span>
                  <span className="mx-2">•</span>
                  <span>{formatDate(item.reportedAt)}</span>
                </div>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadgeClass(item.status)}`}>
                {item.status}
              </span>
            </div>
            <p className="text-sm mb-4 border-l-2 border-muted pl-3 py-1 italic">
              {item.content}
            </p>
            <div className="flex justify-end gap-2">
              {item.status === 'pending' && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleResolveFlaggedContent(item.id)}
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Mark as Resolved
                </Button>
              )}
              <Button 
                variant="outline" 
                size="sm"
                className="text-red-600"
                onClick={() => handleDeleteFlaggedContent(item.id)}
              >
                <Trash className="h-4 w-4 mr-1" />
                Delete
              </Button>
            </div>
          </div>
        ))}
        {filteredFlaggedContent.length === 0 && (
          <div className="p-4 text-center text-muted-foreground border rounded-md">
            No flagged content found.
          </div>
        )}
      </div>
    </div>
  );
  
  // Render feeds tab
  const renderFeedsTab = () => (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="relative w-64">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search feeds..."
            className="pl-8 pr-4 py-2 w-full rounded-md border border-input bg-background"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleSyncFeeds} disabled={isSyncingFeeds}>
            {isSyncingFeeds ? (
              <>
                <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                Syncing...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-1" />
                Sync All Feeds
              </>
            )}
          </Button>
          <Button onClick={() => setIsAddingFeed(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Add Feed
          </Button>
        </div>
      </div>
      
      {isAddingFeed && (
        <div className="mb-4 p-4 border rounded-md bg-muted/20">
          <h3 className="font-medium mb-3">Add New Feed</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="feedName" className="block text-sm font-medium mb-1">Feed Name</label>
              <input
                type="text"
                id="feedName"
                value={newFeed.name}
                onChange={(e) => setNewFeed({ ...newFeed, name: e.target.value })}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="feedSource" className="block text-sm font-medium mb-1">Source</label>
              <select
                id="feedSource"
                value={newFeed.source}
                onChange={(e) => setNewFeed({ ...newFeed, source: e.target.value })}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="arxiv">ArXiv</option>
                <option value="youtube">YouTube</option>
                <option value="rss">RSS</option>
              </select>
            </div>
            
            {newFeed.source === 'arxiv' && (
              <div>
                <label htmlFor="category" className="block text-sm font-medium mb-1">ArXiv Category</label>
                <input
                  type="text"
                  id="category"
                  value={newFeed.category}
                  onChange={(e) => setNewFeed({ ...newFeed, category: e.target.value })}
                  placeholder="e.g., cs.LG, cs.AI"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
            )}
            
            {newFeed.source === 'youtube' && (
              <div>
                <label htmlFor="channel" className="block text-sm font-medium mb-1">YouTube Channel</label>
                <input
                  type="text"
                  id="channel"
                  value={newFeed.channel}
                  onChange={(e) => setNewFeed({ ...newFeed, channel: e.target.value })}
                  placeholder="Channel ID or username"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
            )}
            
            {newFeed.source === 'rss' && (
              <div>
                <label htmlFor="url" className="block text-sm font-medium mb-1">RSS URL</label>
                <input
                  type="text"
                  id="url"
                  value={newFeed.url}
                  onChange={(e) => setNewFeed({ ...newFeed, url: e.target.value })}
                  placeholder="https://example.com/feed"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
            )}
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" size="sm" onClick={() => setIsAddingFeed(false)}>
              <X className="h-4 w-4 mr-1" />
              Cancel
            </Button>
            <Button size="sm" onClick={handleAddFeed}>
              <Check className="h-4 w-4 mr-1" />
              Add Feed
            </Button>
          </div>
        </div>
      )}
      
      <div className="space-y-4">
        {filteredFeeds.map(feed => (
          <div key={feed.id} className="border rounded-md p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-medium">{feed.name}</h3>
                <div className="flex items-center text-sm text-muted-foreground mt-1">
                  <span className="capitalize">{feed.source}</span>
                  {feed.source === 'arxiv' && feed.category && (
                    <>
                      <span className="mx-2">•</span>
                      <span>{feed.category}</span>
                    </>
                  )}
                  {feed.source === 'youtube' && feed.channel && (
                    <>
                      <span className="mx-2">•</span>
                      <span>{feed.channel}</span>
                    </>
                  )}
                  {feed.source === 'rss' && feed.url && (
                    <>
                      <span className="mx-2">•</span>
                      <span className="truncate max-w-xs">{feed.url}</span>
                    </>
                  )}
                </div>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadgeClass(feed.status)}`}>
                {feed.status}
              </span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <div>
                <span className="text-muted-foreground">Last synced: {formatDate(feed.lastSync)}</span>
                <span className="mx-2">•</span>
                <span>{feed.itemCount} items</span>
              </div>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleDeleteFeed(feed.id)}
                >
                  <Trash className="h-4 w-4 mr-1" />
                  Delete
                </Button>
              </div>
            </div>
          </div>
        ))}
        {filteredFeeds.length === 0 && (
          <div className="p-4 text-center text-muted-foreground border rounded-md">
            No feeds found.
          </div>
        )}
      </div>
    </div>
  );
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center mb-6">
        <Button variant="ghost" size="sm" onClick={onBack} className="mr-2">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Admin Panel</h1>
      </div>
      
      <div className="flex border-b mb-6">
        <button
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'users' ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}
          onClick={() => {
            setActiveTab('users');
            setSearchTerm('');
          }}
        >
          <Users className="h-4 w-4 inline mr-1" />
          Users
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'flagged' ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}
          onClick={() => {
            setActiveTab('flagged');
            setSearchTerm('');
          }}
        >
          <Flag className="h-4 w-4 inline mr-1" />
          Flagged Content
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'feeds' ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}
          onClick={() => {
            setActiveTab('feeds');
            setSearchTerm('');
          }}
        >
          <Rss className="h-4 w-4 inline mr-1" />
          Feeds Sync
        </button>
      </div>
      
      <div className="flex-1">
        {activeTab === 'users' && renderUsersTab()}
        {activeTab === 'flagged' && renderFlaggedContentTab()}
        {activeTab === 'feeds' && renderFeedsTab()}
      </div>
    </div>
  );
};

export default AdminPanel;