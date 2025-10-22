import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Spinner,
  Alert,
  Button,
} from "react-bootstrap";

import { ROUTE_AUTHOR_LIST, ROUTE_AUTHOR_EDIT } from "../../../constants";
import { useAuthors } from "../../../hooks/useAuthors";
import { formatApiError } from "../../../utils/error";

const AuthorView = () => {
  const { authorId } = useParams();
  const { getAuthorById } = useAuthors();
  const [author, setAuthor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAuthor = async () => {
      setLoading(true);
      setError(null);

      try {
        const authorData = await getAuthorById(authorId);
        setAuthor(authorData);
      } catch (err) {
        const message =
          err.formattedMessage || formatApiError(err, "Failed to load author");
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    if (authorId) {
      fetchAuthor();
    }
  }, [authorId, getAuthorById]);

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
              <Button
                as={Link}
                to={ROUTE_AUTHOR_LIST}
                variant="outline-secondary"
              >
                Back to Authors
              </Button>
            </Alert>
          </Col>
        </Row>
      </Container>
    );
  }

  if (!author) {
    return null;
  }

  const editUrl = ROUTE_AUTHOR_EDIT.replace(":authorId", author.id);

  return (
    <Container className="mt-4">
      <Row>
        <Col lg={8} md={10} className="mx-auto">
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h3 className="mb-0">{author.full_name}</h3>
              <div className="d-flex gap-2">
                <Button
                  as={Link}
                  to={ROUTE_AUTHOR_LIST}
                  variant="outline-secondary"
                >
                  Back to Authors
                </Button>
                <Button as={Link} to={editUrl} variant="primary">
                  Edit Author
                </Button>
              </div>
            </Card.Header>
            <Card.Body>
              <section className="mb-4">
                <h5 className="text-uppercase text-muted fs-6">First Name</h5>
                <p className="mb-0">{author.first_name}</p>
              </section>
              <section className="mb-4">
                <h5 className="text-uppercase text-muted fs-6">Last Name</h5>
                <p className="mb-0">{author.last_name}</p>
              </section>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default AuthorView;
