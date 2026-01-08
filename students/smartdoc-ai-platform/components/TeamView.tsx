import React from 'react';
import { Users, Github, Linkedin, Award } from 'lucide-react';

export const TeamView: React.FC = () => {
 
  const teamMembers = [
    {
      name: "Faiyaz Ahmed",
      role: "AI & System Architect",
      initials: "F",
      desc: "Specialized in Knowledge Representation and Gemini Integration."
    },
    {
      name: "Abrar Al Rashid and Hesam Zoveidavian Poor",
      role: "UI/UX & React Specialist",
      initials: "A",
      desc: "Designed the responsive interface and user experience flow."
    },
    {
      name: "Mahmoud Ali Balawee",
      role: "Validation and Rules",
      initials: "M",
      desc: "Developed the validation rules and risk assessment logic."
    },
    {
        name: "Hussein Nazif Ar Rifai",
        role: "API & Data Management",
        initials: "H",
        desc: "Ensured secure data handling and efficient processing."
      }
  ];

  return (
    <div className="max-w-7xl mx-auto w-full animate-in fade-in duration-500">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Meet The Team</h2>
        <p className="text-gray-500 max-w-2xl mx-auto">
          The minds behind the SmartDoc Platform. A collaborative effort for the UTM Artificial Intelligence Project.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {teamMembers.map((member, idx) => (
          <div key={idx} className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 flex flex-col items-center text-center hover:shadow-md transition-shadow group">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 text-blue-600 flex items-center justify-center text-2xl font-bold mb-4 border-4 border-white shadow-sm group-hover:scale-110 transition-transform">
              {member.initials}
            </div>
            <h3 className="text-lg font-bold text-gray-900">{member.name}</h3>
            <span className="inline-block px-3 py-1 bg-gray-100 text-gray-600 text-xs font-semibold rounded-full mt-2 mb-4">
              {member.role}
            </span>
            <p className="text-sm text-gray-500 mb-6 flex-1">
              {member.desc}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-16 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 lg:p-12 text-white text-center relative overflow-hidden">
        <div className="relative z-10">
          <Users size={48} className="mx-auto mb-4 opacity-80" />
          <h3 className="text-2xl font-bold mb-2">Project Vision</h3>
          <p className="max-w-2xl mx-auto text-blue-100">
            "To simplify document management through intelligent automation and robust knowledge representation."
          </p>
        </div>
        {/* Decorative circles */}
        <div className="absolute top-0 left-0 w-64 h-64 bg-white opacity-5 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full translate-x-1/2 translate-y-1/2"></div>
      </div>
    </div>
  );
};
