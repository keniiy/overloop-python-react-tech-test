import React, { useState } from 'react';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';

function AuthorForm({ 
  initialData = { first_name: '', last_name: '' }, 
  onSubmit, 
  loading = false, 
  error = null,
  submitText = 'Save Author'
}) {
  const [formData, setFormData] = useState(initialData);
  const [validationErrors, setValidationErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.first_name.trim()) {
      errors.first_name = 'First name is required';
    } else if (formData.first_name.trim().length < 2) {
      errors.first_name = 'First name must be at least 2 characters';
    }
    
    if (!formData.last_name.trim()) {
      errors.last_name = 'Last name is required';
    } else if (formData.last_name.trim().length < 2) {
      errors.last_name = 'Last name must be at least 2 characters';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit({
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim()
      });
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      {error && (
        <Alert variant="danger" className="mb-3">
          {error}
        </Alert>
      )}
      
      <Form.Group className="mb-3">
        <Form.Label>First Name *</Form.Label>
        <Form.Control
          type="text"
          name="first_name"
          value={formData.first_name}
          onChange={handleChange}
          isInvalid={!!validationErrors.first_name}
          placeholder="Enter first name"
          disabled={loading}
        />
        <Form.Control.Feedback type="invalid">
          {validationErrors.first_name}
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Last Name *</Form.Label>
        <Form.Control
          type="text"
          name="last_name"
          value={formData.last_name}
          onChange={handleChange}
          isInvalid={!!validationErrors.last_name}
          placeholder="Enter last name"
          disabled={loading}
        />
        <Form.Control.Feedback type="invalid">
          {validationErrors.last_name}
        </Form.Control.Feedback>
      </Form.Group>

      <div className="d-flex gap-2">
        <Button 
          type="submit" 
          variant="primary" 
          disabled={loading}
        >
          {loading && (
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
              className="me-2"
            />
          )}
          {submitText}
        </Button>
      </div>
    </Form>
  );
}

export default AuthorForm;