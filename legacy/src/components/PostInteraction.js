import React, { useState } from 'react';
import { MessageCircle, Heart, Send, Loader2, ExternalLink } from 'lucide-react';
import axios from 'axios';

const PostInteraction = () => {
  const [postUrl, setPostUrl] = useState('');
  const [action, setAction] = useState('like');
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleInteraction = async (e) => {
    e.preventDefault();
    if (!postUrl.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('/api/interact_with_linkedin_post', {
        post_url: postUrl.trim(),
        action: action,
        comment: comment.trim() || undefined
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Interaction failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Post Interaction</h1>
        <p className="text-gray-600">
          Like, comment, or interact with LinkedIn posts
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleInteraction} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Post URL
            </label>
            <input
              type="url"
              value={postUrl}
              onChange={(e) => setPostUrl(e.target.value)}
              placeholder="https://www.linkedin.com/posts/..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-linkedin-500"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Action
              </label>
              <select
                value={action}
                onChange={(e) => setAction(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-linkedin-500"
              >
                <option value="like">Like Post</option>
                <option value="comment">Comment on Post</option>
                <option value="read">Read Post Content</option>
              </select>
            </div>

            {action === 'comment' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Comment
                </label>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Enter your comment..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-linkedin-500"
                  required
                />
              </div>
            )}
          </div>

          <div className="flex items-center justify-between">
            <button
              type="submit"
              disabled={loading || !postUrl.trim()}
              className="flex items-center justify-center space-x-2 px-6 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : action === 'like' ? (
                <Heart className="w-5 h-5" />
              ) : action === 'comment' ? (
                <MessageCircle className="w-5 h-5" />
              ) : (
                <ExternalLink className="w-5 h-5" />
              )}
              <span>
                {loading ? 'Processing...' : 
                 action === 'like' ? 'Like Post' :
                 action === 'comment' ? 'Comment on Post' : 'Read Post'}
              </span>
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-medium text-green-900 mb-2">Success!</h3>
          <div className="text-sm text-green-800 space-y-1">
            {result.success && <p>✅ Action completed successfully</p>}
            {result.message && <p>{result.message}</p>}
            {result.post_content && (
              <div className="mt-3 p-3 bg-white rounded border border-green-200">
                <h4 className="font-medium text-green-900 mb-2">Post Content:</h4>
                <p className="text-gray-700">{result.post_content}</p>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">How to use:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• <strong>Like Post:</strong> Automatically like the specified LinkedIn post</li>
          <li>• <strong>Comment on Post:</strong> Add a comment to the specified post</li>
          <li>• <strong>Read Post Content:</strong> Extract and display the post content</li>
          <li>• Copy the LinkedIn post URL from your browser and paste it above</li>
        </ul>
      </div>
    </div>
  );
};

export default PostInteraction; 