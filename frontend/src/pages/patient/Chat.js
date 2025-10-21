import React, { useContext, useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext, API } from '@/App';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowLeft, Send } from 'lucide-react';
import Layout from '@/components/Layout';
import { toast } from 'sonner';

export default function PatientChat() {
  const { appointmentId } = useParams();
  const navigate = useNavigate();
  const { user, token } = useContext(AuthContext);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  }, [appointmentId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchMessages = async () => {
    try {
      const response = await axios.get(`${API}/chat/${appointmentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      await axios.post(`${API}/chat/send`, {
        appointment_id: appointmentId,
        message: newMessage
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNewMessage('');
      fetchMessages();
    } catch (error) {
      toast.error('Không thể gửi tin nhắn');
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-teal-50 to-blue-50 p-6">
        <div className="max-w-4xl mx-auto">
          <Button data-testid="back-btn" variant="ghost" onClick={() => navigate('/patient/appointments')} className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Quay lại
          </Button>

          <div className="bg-white rounded-3xl shadow-xl overflow-hidden">
            <div className="bg-gradient-to-r from-teal-500 to-cyan-500 p-6">
              <h1 className="text-2xl font-bold text-white">Tư vấn trực tuyến</h1>
            </div>

            <div className="h-[500px] overflow-y-auto p-6 space-y-4" data-testid="chat-messages">
              {loading ? (
                <p className="text-center text-gray-500">Đang tải...</p>
              ) : messages.length === 0 ? (
                <p className="text-center text-gray-500">Chưa có tin nhắn nào</p>
              ) : (
                messages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} isOwn={msg.sender_id === user?.id} />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSendMessage} className="border-t p-4 flex gap-3">
              <Input
                data-testid="message-input"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Nhập tin nhắn..."
                className="flex-1"
              />
              <Button data-testid="send-btn" type="submit" className="bg-gradient-to-r from-teal-500 to-cyan-500">
                <Send className="w-5 h-5" />
              </Button>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
}

function MessageBubble({ message, isOwn }) {
  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[70%] rounded-2xl px-4 py-3 ${
        isOwn 
          ? 'bg-gradient-to-r from-teal-500 to-cyan-500 text-white' 
          : 'bg-gray-100 text-gray-900'
      }`}>
        <p className="font-semibold text-sm mb-1">{message.sender_name}</p>
        <p>{message.message}</p>
        <p className={`text-xs mt-1 ${isOwn ? 'text-white/70' : 'text-gray-500'}`}>
          {new Date(message.created_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}
