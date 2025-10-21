import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Table, Spinner, Alert, Form } from 'react-bootstrap';
import { useAuthors } from '../../../hooks/useAuthors';
import { ROUTE_AUTHOR_CREATE, ROUTE_AUTHOR_EDIT } from '../../../constants';

function AuthorList() {
  const { authors, loading, error, fetchAuthors, deleteAuthor, searchAuthors } = useAuthors();
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAuthors();
  }, [fetchAuthors]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      searchAuthors(searchTerm);
    } else {
      fetchAuthors();
    }
  };

  const handleDelete = async (id, fullName) => {
    if (window.confirm(`Are you sure you want to delete ${fullName}?`)) {
      try {
        await deleteAuthor(id);
      } catch (error) {
        // Error notification handled by hook
      }
    }
  };

  const editUrl = (authorId) => ROUTE_AUTHOR_EDIT.replace(':authorId', authorId);

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h3 className="mb-0">Authors</h3>
              <Button as={Link} to={ROUTE_AUTHOR_CREATE} variant="primary">
                Add New Author
              </Button>
            </Card.Header>
            <Card.Body>
              {/* Search Form */}
              <Form onSubmit={handleSearch} className="mb-3">
                <Row>
                  <Col md={8}>
                    <Form.Control
                      type="text"
                      placeholder="Search authors by name..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </Col>
                  <Col md={4}>
                    <div className="d-flex gap-2">
                      <Button type="submit" variant="outline-primary">
                        Search
                      </Button>
                      <Button 
                        type="button" 
                        variant="outline-secondary"
                        onClick={() => {
                          setSearchTerm('');
                          fetchAuthors();
                        }}
                      >
                        Clear
                      </Button>
                    </div>
                  </Col>
                </Row>
              </Form>

              {/* Loading State */}
              {loading && (
                <div className="text-center">
                  <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </Spinner>
                </div>
              )}

              {/* Error State */}
              {error && (
                <Alert variant="danger">
                  Error loading authors: {error}
                </Alert>
              )}

              {/* Authors Table */}
              {!loading && !error && (
                <>
                  {authors.length === 0 ? (
                    <Alert variant="info">
                      No authors found. {searchTerm && 'Try a different search term or '} 
                      <Link to={ROUTE_AUTHOR_CREATE}>Add the first author</Link>.
                    </Alert>
                  ) : (
                    <Table striped bordered hover responsive>
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Name</th>
                          <th>First Name</th>
                          <th>Last Name</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {authors.map((author) => (
                          <tr key={author.id}>
                            <td>{author.id}</td>
                            <td><strong>{author.full_name}</strong></td>
                            <td>{author.first_name}</td>
                            <td>{author.last_name}</td>
                            <td>
                              <div className="d-flex gap-2">
                                <Button
                                  as={Link}
                                  to={editUrl(author.id)}
                                  variant="outline-primary"
                                  size="sm"
                                >
                                  Edit
                                </Button>
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => handleDelete(author.id, author.full_name)}
                                >
                                  Delete
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  )}
                  
                  {authors.length > 0 && (
                    <div className="mt-3 text-muted">
                      Showing {authors.length} author{authors.length !== 1 ? 's' : ''}
                    </div>
                  )}
                </>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default AuthorList;