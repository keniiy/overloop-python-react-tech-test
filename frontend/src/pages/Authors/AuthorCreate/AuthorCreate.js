import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import AuthorForm from '../../../components/forms/AuthorForm/AuthorForm';
import { useAuthors } from '../../../hooks/useAuthors';
import { ROUTE_AUTHOR_LIST } from '../../../constants';

function AuthorCreate() {
  const navigate = useNavigate();
  const { createAuthor } = useAuthors();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (authorData) => {
    setLoading(true);
    setError(null);
    
    try {
      await createAuthor(authorData);
      navigate(ROUTE_AUTHOR_LIST);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to create author');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="mt-4">
      <Row>
        <Col lg={8} md={10} className="mx-auto">
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h3 className="mb-0">Create New Author</h3>
              <Button as={Link} to={ROUTE_AUTHOR_LIST} variant="outline-secondary">
                Back to Authors
              </Button>
            </Card.Header>
            <Card.Body>
              <AuthorForm
                onSubmit={handleSubmit}
                loading={loading}
                error={error}
                submitText="Create Author"
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default AuthorCreate;