import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './FeedbackModal.css';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (feedback: { message: string; email?: string }) => Promise<void>;
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const { t } = useTranslation();
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim()) {
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      await onSubmit({
        message: message.trim(),
        email: email.trim() || undefined
      });
      setSubmitStatus('success');
      setMessage('');
      setEmail('');
      
      // Close modal after a brief delay to show success message
      setTimeout(() => {
        onClose();
        setSubmitStatus('idle');
      }, 3000);
    } catch (error) {
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setMessage('');
      setEmail('');
      setSubmitStatus('idle');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="feedback-modal-overlay" onClick={handleClose}>
      <div className="feedback-modal" onClick={(e) => e.stopPropagation()}>
        <div className="feedback-modal-header">
          <h2>{t('feedback.title')}</h2>
          <button 
            className="feedback-modal-close" 
            onClick={handleClose}
            disabled={isSubmitting}
          >
            ×
          </button>
        </div>

        <div className="feedback-modal-content">
          {submitStatus === 'success' ? (
            <div className="feedback-success">
              <p>{t('feedback.success')}</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="feedback-field">
                <label htmlFor="feedback-message">
                  {t('feedback.messageLabel')} *
                </label>
                <textarea
                  id="feedback-message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder={t('feedback.messagePlaceholder')}
                  rows={5}
                  required
                  disabled={isSubmitting}
                />
              </div>

              <div className="feedback-field">
                <label htmlFor="feedback-email">
                  {t('feedback.emailLabel')}
                </label>
                <input
                  id="feedback-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t('feedback.emailPlaceholder')}
                  disabled={isSubmitting}
                />
              </div>

              {submitStatus === 'error' && (
                <div className="feedback-error">
                  {t('feedback.error')}
                </div>
              )}

              <div className="feedback-modal-actions">
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={isSubmitting}
                  className="feedback-button feedback-button-secondary"
                >
                  {t('feedback.cancel')}
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !message.trim()}
                  className="feedback-button feedback-button-primary"
                >
                  {isSubmitting ? t('feedback.sending') : t('feedback.send')}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default FeedbackModal;
