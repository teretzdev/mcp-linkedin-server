import React, { useState } from 'react';
import { Activity, Eye, Heart, MessageCircle, Share, Loader2, RefreshCw } from 'lucide-react';
import axios from 'axios';

const FeedBrowser = () => {
  const [count, setCount] = useState(5);
  const [loading, setLoading] = useState(false);
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState('');

  const handleBrowseFeed = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setPosts([]);

    try {
      const response = await axios.post('/api/browse_linkedin_feed', {
        count: parseInt(count)
      });
      setPosts(response.data.posts || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to browse feed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    if (!loading) {
      handleBrowseFeed({ preventDefault: () => {} });
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Feed Browser</h1>
        <p className="text-gray-600">
          Browse and view posts from your LinkedIn feed
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleBrowseFeed} className="space-y-4">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Posts
              </label>
              <select
                value={count}
                onChange={(e) => setCount(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-linkedin-500"
              >
                <option value={5}>5 posts</option>
                <option value={10}>10 posts</option>
                <option value={15}>15 posts</option>
                <option value={20}>20 posts</option>
              </select>
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="flex items-center justify-center space-x-2 px-6 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Activity className="w-5 h-5" />
              )}
              <span>{loading ? 'Loading...' : 'Browse Feed'}</span>
            </button>

            {posts.length > 0 && (
              <button
                type="button"
                onClick={handleRefresh}
                disabled={loading}
                className="flex items-center justify-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
            )}
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {posts.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Feed Posts ({posts.length})
          </h2>
          <div className="space-y-4">
            {posts.map((post, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 bg-linkedin-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Activity className="w-5 h-5 text-linkedin-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium text-gray-900">
                        {post.author || 'Unknown Author'}
                      </h3>
                      {post.timestamp && (
                        <span className="text-xs text-gray-500">
                          {new Date(post.timestamp).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    
                    {post.content && (
                      <p className="text-gray-700 mb-3 line-clamp-3">
                        {post.content}
                      </p>
                    )}

                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      {post.likes && (
                        <div className="flex items-center space-x-1">
                          <Heart className="w-4 h-4" />
                          <span>{post.likes}</span>
                        </div>
                      )}
                      {post.comments && (
                        <div className="flex items-center space-x-1">
                          <MessageCircle className="w-4 h-4" />
                          <span>{post.comments}</span>
                        </div>
                      )}
                      {post.shares && (
                        <div className="flex items-center space-x-1">
                          <Share className="w-4 h-4" />
                          <span>{post.shares}</span>
                        </div>
                      )}
                      {post.views && (
                        <div className="flex items-center space-x-1">
                          <Eye className="w-4 h-4" />
                          <span>{post.views}</span>
                        </div>
                      )}
                    </div>

                    {post.url && (
                      <a
                        href={post.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-1 mt-2 text-xs text-linkedin-600 hover:text-linkedin-700"
                      >
                        <span>View Original Post</span>
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="w-6 h-6 animate-spin text-linkedin-600" />
            <span className="text-gray-600">Loading LinkedIn feed...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedBrowser; 