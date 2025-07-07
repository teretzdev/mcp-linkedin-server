import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, Heart, MessageCircle, Share2, User } from 'lucide-react';
import axios from 'axios';

function FeedBrowser() {
  const [feedPosts, setFeedPosts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredPosts, setFilteredPosts] = useState([]);

  useEffect(() => {
    fetchFeed();
  }, []);

  useEffect(() => {
    filterPosts();
  }, [feedPosts, searchQuery]);

  const fetchFeed = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('/api/linkedin_feed');
      setFeedPosts(response.data.posts || []);
    } catch (error) {
      console.error('Failed to fetch feed:', error);
      setFeedPosts([]);
    } finally {
      setIsLoading(false);
    }
  };

  const filterPosts = () => {
    if (!searchQuery.trim()) {
      setFilteredPosts(feedPosts);
      return;
    }

    const filtered = feedPosts.filter(post =>
      post.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.company?.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredPosts(filtered);
  };

  const handleInteraction = async (postId, interactionType) => {
    try {
      await axios.post('/api/interact_with_post', {
        post_id: postId,
        interaction_type: interactionType
      });
      // Update local state to reflect the interaction
      setFeedPosts(prev => prev.map(post => 
        post.id === postId 
          ? { ...post, [interactionType]: (post[interactionType] || 0) + 1 }
          : post
      ));
    } catch (error) {
      console.error('Interaction failed:', error);
    }
  };

  return (
    <div className="container container-lg">
      <div className="p-xl">
        <div className="card">
          <div className="card-header">
            <h1 className="text-2xl font-bold text-primary">Feed Browser</h1>
            <p className="text-secondary">
              Browse and interact with LinkedIn feed posts
            </p>
          </div>
          
          <div className="card-body">
            {/* Search and Controls */}
            <div className="card mb-lg">
              <div className="card-body">
                <div className="flex flex-col md:flex-row gap-md">
                  <div className="flex-1">
                    <label className="form-label">Search Posts</label>
                    <div className="relative">
                      <Search className="absolute left-md top-1/2 transform -translate-y-1/2 w-5 h-5 text-tertiary" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search posts, authors, or companies..."
                        className="form-input pl-xl"
                      />
                    </div>
                  </div>
                  <div className="flex items-end">
                    <button
                      onClick={fetchFeed}
                      disabled={isLoading}
                      className="btn btn-secondary flex items-center gap-sm"
                    >
                      <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                      {isLoading ? 'Loading...' : 'Refresh Feed'}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Feed Posts */}
            {filteredPosts.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-primary">
                    Feed Posts ({filteredPosts.length})
                  </h2>
                </div>
                <div className="card-body">
                  <div className="space-y-lg">
                    {filteredPosts.map((post, index) => (
                      <div key={index} className="card">
                        <div className="card-body">
                          {/* Post Header */}
                          <div className="flex items-start gap-md mb-md">
                            <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                              {post.author?.charAt(0) || 'U'}
                            </div>
                            <div className="flex-1 min-w-0">
                              <h3 className="font-medium text-primary">
                                {post.author || 'Unknown Author'}
                              </h3>
                              <span className="text-xs text-tertiary">
                                {post.timestamp || 'Unknown time'}
                              </span>
                            </div>
                          </div>

                          {/* Post Content */}
                          <p className="text-primary mb-md line-clamp-3">
                            {post.content || 'No content available'}
                          </p>

                          {/* Post Stats */}
                          <div className="flex items-center gap-lg text-sm text-tertiary mb-md">
                            <span>{post.likes || 0} likes</span>
                            <span>{post.comments || 0} comments</span>
                            <span>{post.shares || 0} shares</span>
                          </div>

                          {/* Interaction Buttons */}
                          <div className="flex gap-sm">
                            <button
                              onClick={() => handleInteraction(post.id, 'likes')}
                              className="btn btn-secondary btn-sm flex items-center gap-xs"
                            >
                              <Heart className="w-4 h-4" />
                              Like
                            </button>
                            <button
                              onClick={() => handleInteraction(post.id, 'comments')}
                              className="btn btn-secondary btn-sm flex items-center gap-xs"
                            >
                              <MessageCircle className="w-4 h-4" />
                              Comment
                            </button>
                            <button
                              onClick={() => handleInteraction(post.id, 'shares')}
                              className="btn btn-secondary btn-sm flex items-center gap-xs"
                            >
                              <Share2 className="w-4 h-4" />
                              Share
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="card">
                <div className="card-body text-center py-xl">
                  <span className="text-secondary">Loading LinkedIn feed...</span>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && filteredPosts.length === 0 && searchQuery && (
              <div className="card">
                <div className="card-body text-center py-xl">
                  <span className="text-secondary">No posts found matching your search.</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default FeedBrowser; 