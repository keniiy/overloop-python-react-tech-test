import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';
import Alert from 'react-bootstrap/Alert';
import Badge from 'react-bootstrap/Badge';

import {
    ROUTE_ARTICLE_CREATE,
    ROUTE_ARTICLE_VIEW,
    ROUTE_ARTICLE_EDIT,
} from '../../../constants';
import { listArticles } from '../../../services/articles';
import PaginationControls from '../../../components/PaginationControls/PaginationControls';

const DEFAULT_LIMIT = 10;

function ArticleList() {
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [pagination, setPagination] = useState({
        current_page: 1,
        total_pages: 1,
        total_items: 0,
        per_page: DEFAULT_LIMIT,
        has_next: false,
        has_prev: false
    });

    const fetchArticles = useCallback(async (nextPage = 1) => {
        setLoading(true);
        setError(null);

        try {
            const response = await listArticles({ page: nextPage, limit: DEFAULT_LIMIT });
            setArticles(response.data || []);
            setPagination({
                current_page: response.pagination?.current_page ?? nextPage,
                total_pages: response.pagination?.total_pages ?? 1,
                total_items: response.pagination?.total_items ?? 0,
                per_page: response.pagination?.per_page ?? DEFAULT_LIMIT,
                has_next: response.pagination?.has_next ?? false,
                has_prev: response.pagination?.has_prev ?? false
            });
        } catch (fetchError) {
            setError(fetchError.response?.data?.error || fetchError.message || 'Failed to load articles');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchArticles(page);
    }, [fetchArticles, page]);

    const handlePrevPage = () => {
        if (pagination.has_prev) {
            setPage((prev) => Math.max(1, prev - 1));
        }
    };

    const handleNextPage = () => {
        if (pagination.has_next) {
            setPage((prev) => prev + 1);
        }
    };

    const renderArticles = () => {
        if (articles.length === 0) {
            return (
                <tr>
                    <td colSpan={ 5 } className="text-center text-muted py-4">
                        No articles found.
                    </td>
                </tr>
            );
        }

        const offset = (pagination.current_page - 1) * (pagination.per_page || DEFAULT_LIMIT);

        return articles.map((article, index) => {
            const { id, title, author, regions } = article;
            const authorName = author?.full_name || (author ? `${author.first_name} ${author.last_name}` : '');
            const rowNumber = offset + index + 1;

            return (
                <tr key={ id }>
                    <td>{rowNumber}</td>
                    <td className="fw-semibold">
                        <Link to={ ROUTE_ARTICLE_VIEW.replace(':articleId', id) }>{ title }</Link>
                    </td>
                    <td>{ authorName || <span className="text-muted">No author</span> }</td>
                    <td className="text-nowrap">
                        {regions && regions.length > 0 ? (
                            regions.map((region) => (
                                <Badge bg="secondary" key={ region.id } className="me-1 mb-1">
                                    {region.name}
                                </Badge>
                            ))
                        ) : (
                            <span className="text-muted">No regions</span>
                        )}
                    </td>
                    <td>
                        <div className="d-flex gap-2">
                            <Button
                                as={Link}
                                to={ ROUTE_ARTICLE_VIEW.replace(':articleId', id) }
                                variant="outline-secondary"
                                size="sm"
                            >
                                View
                            </Button>
                            <Button
                                as={Link}
                                to={ ROUTE_ARTICLE_EDIT.replace(':articleId', id) }
                                variant="outline-primary"
                                size="sm"
                            >
                                Edit
                            </Button>
                        </div>
                    </td>
                </tr>
            );
        });
    };

    return (
        <div className="ArticleList">
            <div className="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
                <h1 className="mb-0">Articles</h1>
                <div className="d-grid d-sm-inline">
                    <Link className="btn btn-primary" to={ ROUTE_ARTICLE_CREATE }>
                        Create a new Article
                    </Link>
                </div>
            </div>

            {error && (
                <Alert variant="danger" className="mt-3">
                    {error}
                </Alert>
            )}

            <div className="mt-3">
                <Table striped bordered hover responsive="md">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Title</th>
                            <th>Author</th>
                            <th>Regions</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan={ 5 } className="text-center py-4">
                                    <Spinner animation="border" role="status">
                                        <span className="visually-hidden">Loading articles...</span>
                                    </Spinner>
                                    <div className="mt-2 text-muted">Loading articles...</div>
                                </td>
                            </tr>
                        ) : (
                            renderArticles()
                        )}
                    </tbody>
                </Table>
            </div>

            <PaginationControls
                pagination={ pagination }
                onPrev={ handlePrevPage }
                onNext={ handleNextPage }
                disabled={ loading }
            />
        </div>
    );
}

export default ArticleList;
