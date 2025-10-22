import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Badge, Spinner, Alert, Button } from 'react-bootstrap';

import { ROUTE_ARTICLE_LIST, ROUTE_ARTICLE_EDIT } from '../../../constants';
import { getArticle } from '../../../services/articles';
import { formatApiError } from '../../../utils/error';

const ArticleView = () => {
  const { articleId } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchArticle = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getArticle(articleId);
        setArticle(data);
      } catch (err) {
        const message = formatApiError(err, 'Failed to load article');
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    if (articleId) {
      fetchArticle();
    }
  }, [articleId]);

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading article...</span>
          </Spinner>
          <p className="mt-2">Loading article details...</p>
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
              <h5>Error Loading Article</h5>
              <p>{ error }</p>
              <Button variant="outline-secondary" onClick={() => navigate(ROUTE_ARTICLE_LIST)}>
                Back to Articles
              </Button>
            </Alert>
          </Col>
        </Row>
      </Container>
    );
  }

  if (!article) {
    return null;
  }

  const editUrl = ROUTE_ARTICLE_EDIT.replace(':articleId', article.id);

  return (
    <Container className="mt-4">
      <Row>
        <Col lg={8} md={10} className="mx-auto">
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <div>
                <h3 className="mb-1">{article.title}</h3>
                <div className="text-muted">
                  {article.author
                    ? `by ${article.author.full_name || `${article.author.first_name} ${article.author.last_name}`}`
                    : 'No author'}
                </div>
              </div>
              <div className="d-flex gap-2">
                <Button as={Link} to={ROUTE_ARTICLE_LIST} variant="outline-secondary">
                  Back to Articles
                </Button>
                <Button as={Link} to={editUrl} variant="primary">
                  Edit Article
                </Button>
              </div>
            </Card.Header>
            <Card.Body>
              <section className="mb-4">
                <h5 className="text-uppercase text-muted fs-6">Content</h5>
                <p className="mb-0" style={{ whiteSpace: 'pre-line' }}>
                  {article.content}
                </p>
              </section>
              <section className="mb-4">
                <h5 className="text-uppercase text-muted fs-6">Regions</h5>
                {article.regions && article.regions.length > 0 ? (
                  article.regions.map((region) => (
                    <Badge key={region.id} bg="secondary" className="me-2 mb-2">
                      {region.name}
                    </Badge>
                  ))
                ) : (
                  <span className="text-muted">No regions</span>
                )}
              </section>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ArticleView;
