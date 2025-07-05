import React, { useState, useMemo, useEffect } from 'react';
import axios from 'axios';

const DEFAULT_PROFILE = {
  personalInfo: {
    name: '',
    email: '',
    phone: '',
    location: '',
    linkedin: '',
    github: '',
    portfolio: ''
  },
  skills: [],
  experiences: [],
  education: []
};

const ApplicantKnowledgeBase = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSkillLevel, setSelectedSkillLevel] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [profile, setProfile] = useState(DEFAULT_PROFILE);

  useEffect(() => {
    // Fetch applicant profile from backend
    const fetchProfile = async () => {
      try {
        const response = await axios.get('/api/applicant_profile');
        setProfile(response.data || DEFAULT_PROFILE);
      } catch (error) {
        setProfile(DEFAULT_PROFILE);
      }
    };
    fetchProfile();
  }, []);

  // Get unique categories for filter
  const categories = useMemo(() => {
    const cats = [...new Set((profile.skills || []).map(skill => skill.category))];
    return ['all', ...cats];
  }, [profile.skills]);

  // Get unique skill levels for filter
  const skillLevels = useMemo(() => {
    const levels = [...new Set((profile.skills || []).map(skill => skill.level))];
    return ['all', ...levels];
  }, [profile.skills]);

  // Filter and search logic
  const filteredSkills = useMemo(() => {
    return (profile.skills || []).filter(skill => {
      const matchesSearch = skill.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           skill.category.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || skill.category === selectedCategory;
      const matchesLevel = selectedSkillLevel === 'all' || skill.level === selectedSkillLevel;
      
      return matchesSearch && matchesCategory && matchesLevel;
    }).sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'level':
          const levelOrder = { 'Expert': 3, 'Advanced': 2, 'Intermediate': 1, 'Beginner': 0 };
          return levelOrder[b.level] - levelOrder[a.level];
        case 'years':
          return b.years - a.years;
        case 'category':
          return a.category.localeCompare(b.category);
        default:
          return 0;
      }
    });
  }, [profile.skills, searchTerm, selectedCategory, selectedSkillLevel, sortBy]);

  const getLevelColor = (level) => {
    switch (level) {
      case 'Expert': return 'bg-green-100 text-green-800';
      case 'Advanced': return 'bg-blue-100 text-blue-800';
      case 'Intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'Beginner': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const { personalInfo, experiences, education } = profile;

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Applicant Knowledge Base</h1>
          <p className="text-gray-600">Manage your professional profile and preferences</p>
        </div>

        {/* Advanced Search Section */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Advanced Search</h2>
          
          {/* Search Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Search Skills</label>
            <input
              type="text"
              placeholder="Search by skill name or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'All Categories' : category}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Skill Level</label>
              <select
                value={selectedSkillLevel}
                onChange={(e) => setSelectedSkillLevel(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {skillLevels.map(level => (
                  <option key={level} value={level}>
                    {level === 'all' ? 'All Levels' : level}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="name">Name</option>
                <option value="level">Level</option>
                <option value="years">Years of Experience</option>
                <option value="category">Category</option>
              </select>
            </div>
          </div>

          {/* Search Results Summary */}
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>Showing {filteredSkills.length} of {profile.skills.length} skills</span>
            {(searchTerm || selectedCategory !== 'all' || selectedSkillLevel !== 'all') && (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setSelectedCategory('all');
                  setSelectedSkillLevel('all');
                }}
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>
        
        {/* Personal Information */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Personal Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Name</p>
              <p className="font-medium">{personalInfo.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="font-medium">{personalInfo.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Phone</p>
              <p className="font-medium">{personalInfo.phone}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Location</p>
              <p className="font-medium">{personalInfo.location}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">LinkedIn</p>
              <p className="font-medium text-blue-600 hover:text-blue-800 cursor-pointer">{personalInfo.linkedin}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">GitHub</p>
              <p className="font-medium text-blue-600 hover:text-blue-800 cursor-pointer">{personalInfo.github}</p>
            </div>
          </div>
        </div>
        
        {/* Skills with Advanced Search */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Skills</h2>
          {filteredSkills.length > 0 ? (
            <div className="space-y-3">
              {filteredSkills.map((skill, index) => (
                <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-4">
                    <span className="font-medium">{skill.name}</span>
                    <span className={`px-2 py-1 text-sm rounded ${getLevelColor(skill.level)}`}>
                      {skill.level}
                    </span>
                    <span className="text-sm text-gray-500">{skill.years} years</span>
                  </div>
                  <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {skill.category}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No skills match your search criteria.</p>
              <button
                onClick={() => {
                  setSearchTerm('');
                  setSelectedCategory('all');
                  setSelectedSkillLevel('all');
                }}
                className="mt-2 text-blue-600 hover:text-blue-800 underline"
              >
                Clear filters
              </button>
            </div>
          )}
        </div>

        {/* Experience */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Work Experience</h2>
          <div className="space-y-4">
            {experiences.map((exp, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-800">{exp.title}</h3>
                <p className="text-gray-600">{exp.company} • {exp.duration}</p>
                <p className="text-gray-500 text-sm mt-1">{exp.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Education */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Education</h2>
          <div className="space-y-4">
            {education.map((edu, index) => (
              <div key={index} className="border-l-4 border-green-500 pl-4">
                <h3 className="font-semibold text-gray-800">{edu.degree}</h3>
                <p className="text-gray-600">{edu.school} • {edu.year}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApplicantKnowledgeBase;
