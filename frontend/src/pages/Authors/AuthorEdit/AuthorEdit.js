import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Spinner, Alert } from 'react-bootstrap';
import AuthorForm from '../../../components/forms/AuthorForm/AuthorForm';
import { useAuthors } from '../../../hooks/useAuthors';
import { ROUTE_AUTHOR_LIST } from '../../../constants';

function AuthorEdit() {
  const navigate = useNavigate();
  const { authorId } = useParams();
  const { updateAuthor, getAuthorById } = useAuthors();
  
  const [author, setAuthor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submitError, setSubmitError] = useState(null);

  useEffect(() => {
    const fetchAuthor = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const authorData = await getAuthorById(authorId);
        setAuthor(authorData);
      } catch (err) {
        setError(err.response?.data?.error || err.message || 'Failed to fetch author');
      } finally {
        setLoading(false);
      }
    };

    if (authorId) {
      fetchAuthor();
    }
  }, [authorId, getAuthorById]);

  const handleSubmit = async (authorData) => {
    setSubmitLoading(true);
    setSubmitError(null);
    
    try {
      await updateAuthor(authorId, authorData);
      navigate(ROUTE_AUTHOR_LIST);
    } catch (err) {
      setSubmitError(err.response?.data?.error || err.message || 'Failed to update author');
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading author...</span>
          </Spinner>
          <p className="mt-2">Loading author details...</p>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-4">
        <Row>
          <Col lg={8} md={10} className="mx-auto">
            <Alert variant="danger">
              <h5>Error Loading Author</h5>
              <p>{error}</p>
              <Button as={Link} to={ROUTE_AUTHOR_LIST} variant="outline-primary">
                Back to Authors
              </Button>
            </Alert>
          </Col>
        </Row>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row>
        <Col lg={8} md={10} className="mx-auto">
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h3 className="mb-0">
                Edit Author: {author?.full_name}
              </h3>
              <Button as={Link} to={ROUTE_AUTHOR_LIST} variant="outline-secondary">
                Back to Authors
              </Button>
            </Card.Header>
            <Card.Body>
              {author && (
                <AuthorForm
                  initialData={{
                    first_name: author.first_name,
                    last_name: author.last_name
                  }}
                  onSubmit={handleSubmit}
                  loading={submitLoading}
                  error={submitError}
                  submitText="Update Author"
                />
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default AuthorEdit;