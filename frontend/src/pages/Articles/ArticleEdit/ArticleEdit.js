import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';
import Alert from 'react-bootstrap/Alert';

import { ROUTE_ARTICLE_LIST } from '../../../constants';
import { getArticle, editArticle } from '../../../services/articles';
import RegionDropdown from '../../../components/RegionDropdown/RegionDropdown';
import { useAuthors } from '../../../hooks/useAuthors';

function ArticleEdit() {
    const navigate = useNavigate();
    const { articleId } = useParams();
    const { authors, fetchAuthors, loading: authorsLoading, error: authorsError } = useAuthors();

    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [regions, setRegions] = useState([]);
    const [authorId, setAuthorId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [saveError, setSaveError] = useState(null);

    useEffect(() => {
        fetchAuthors();
    }, [fetchAuthors]);

    useEffect(() => {
        const fetchArticle = async () => {
            setLoading(true);
            setError(null);

            try {
                const data = await getArticle(articleId);
                setTitle(data.title);
                setContent(data.content);
                setRegions(data.regions || []);
                setAuthorId(data.author_id ?? null);
            } catch (fetchError) {
                setError(fetchError.response?.data?.error || fetchError.message || 'Failed to load article');
            } finally {
                setLoading(false);
            }
        };

        if (articleId) {
            fetchArticle();
        }
    }, [articleId]);

    const handleAuthorChange = (event) => {
        const value = event.target.value;
        setAuthorId(value === '' ? null : Number(value));
    };

    const handleSave = async (event) => {
        event.preventDefault();
        setSaving(true);
        setSaveError(null);

        try {
            await editArticle(articleId, {
                title,
                content,
                authorId,
                regionIds: regions.map((region) => region.id)
            });
            navigate(ROUTE_ARTICLE_LIST);
        } catch (updateError) {
            setSaveError(updateError.response?.data?.error || updateError.message || 'Failed to update article');
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="ArticleEdit mt-4 text-center">
                <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading article...</span>
                </Spinner>
                <p className="mt-2">Loading article details...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="ArticleEdit mt-4">
                <Alert variant="danger">
                    <h5>Error Loading Article</h5>
                    <p>{ error }</p>
                    <Button variant="outline-secondary" onClick={ () => navigate(ROUTE_ARTICLE_LIST) }>
                        Back to Articles
                    </Button>
                </Alert>
            </div>
        );
    }

    return (
        <div className="ArticleEdit">
            <h1>Edit Article</h1>
            {authorsError && (
                <Alert variant="danger" className="mb-3">
                    Failed to load authors: {authorsError}
                </Alert>
            )}
            {saveError && (
                <Alert variant="danger" className="mb-3">
                    {saveError}
                </Alert>
            )}
            <Form onSubmit={ handleSave }>
            <Form.Group className="mb-3" controlId="articleTitle">
                <Form.Label>Title</Form.Label>
                <Form.Control
                    type="text"
                        placeholder="Title"
                        value={ title }
                        onChange={ (event) => setTitle(event.target.value) }
                        required
                    />
                </Form.Group>
            <Form.Group className="mb-3" controlId="articleContent">
                <Form.Label>Content</Form.Label>
                <Form.Control
                    as="textarea"
                        placeholder="Content"
                        rows="5"
                        value={ content }
                        onChange={ (event) => setContent(event.target.value) }
                        required
                    />
                </Form.Group>
            <Form.Group className="mb-3" controlId="articleAuthor">
                <Form.Label>Author</Form.Label>
                <Form.Select
                    value={ authorId ?? '' }
                        onChange={ handleAuthorChange }
                        disabled={ authorsLoading }
                    >
                        <option value="">No Author</option>
                        {authors.map((author) => (
                            <option key={ author.id } value={ author.id }>
                                {author.full_name || `${author.first_name} ${author.last_name}`}
                            </option>
                        ))}
                    </Form.Select>
                    {authorsLoading && (
                        <div className="mt-2 d-flex align-items-center gap-2 text-muted">
                            <Spinner animation="border" size="sm" role="status" />
                            <span>Loading authors...</span>
                        </div>
                    )}
                </Form.Group>
            <Form.Group className="mb-3" controlId="articleRegions">
                    <Form.Label>Regions</Form.Label>
                    <RegionDropdown
                        value={ regions }
                        onChange={ (selectedRegions) => setRegions(selectedRegions || []) }
                    />
                </Form.Group>
                <Button type="submit" variant="primary" disabled={ saving }>
                    {saving && (
                        <Spinner
                            as="span"
                            animation="border"
                            size="sm"
                            role="status"
                            className="me-2"
                        />
                    )}
                    Save Article
                </Button>
            </Form>
        </div>
    );
}

export default ArticleEdit;
