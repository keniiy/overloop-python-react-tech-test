import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';
import Alert from 'react-bootstrap/Alert';
import Badge from 'react-bootstrap/Badge';

import { ROUTE_ARTICLE_PREFIX, ROUTE_ARTICLE_CREATE } from '../../../constants';
import { listArticles } from '../../../services/articles';

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
                    <td colSpan={ 3 } className="text-center text-muted py-4">
                        No articles found.
                    </td>
                </tr>
            );
        }

        return articles.map((article) => {
            const { id, title, author, regions } = article;
            const authorName = author?.full_name || (author ? `${author.first_name} ${author.last_name}` : '');

            return (
                <tr key={ id }>
                    <td className="fw-semibold">
                        <Link to={ `${ROUTE_ARTICLE_PREFIX}/${id}` }>{ title }</Link>
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
                            <th>Title</th>
                            <th>Author</th>
                            <th>Regions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan={ 3 } className="text-center py-4">
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

            <div className="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3 mt-3">
                <div className="text-muted">
                    Page {pagination.current_page} of {pagination.total_pages} · {pagination.total_items} total
                </div>
                <div className="d-flex gap-2">
                    <Button
                        variant="outline-secondary"
                        onClick={ handlePrevPage }
                        disabled={ !pagination.has_prev || loading }
                    >
                        Previous
                    </Button>
                    <Button
                        variant="outline-secondary"
                        onClick={ handleNextPage }
                        disabled={ !pagination.has_next || loading }
                    >
                        Next
                    </Button>
                </div>
            </div>
        </div>
    );
}

export default ArticleList;
