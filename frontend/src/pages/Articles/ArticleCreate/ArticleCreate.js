import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';
import Alert from 'react-bootstrap/Alert';

import { ROUTE_ARTICLE_LIST } from '../../../constants';
import { createArticle } from '../../../services/articles';
import RegionDropdown from '../../../components/RegionDropdown/RegionDropdown';
import { useAuthors } from '../../../hooks/useAuthors';
import { formatApiError } from '../../../utils/error';

function ArticleCreate() {
    const navigate = useNavigate();
    const { authors, fetchAuthors, loading: authorsLoading, error: authorsError } = useAuthors();

    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [regions, setRegions] = useState([]);
    const [authorId, setAuthorId] = useState(null);
    const [saving, setSaving] = useState(false);
    const [saveError, setSaveError] = useState(null);

    useEffect(() => {
        fetchAuthors({ page: 1, limit: 100, search: undefined });
    }, [fetchAuthors]);

    const handleAuthorChange = (event) => {
        const value = event.target.value;
        setAuthorId(value === '' ? null : Number(value));
    };

    const handleSave = async (event) => {
        event.preventDefault();
        setSaving(true);
        setSaveError(null);

        try {
            await createArticle({
                title,
                content,
                authorId,
                regionIds: regions.map((region) => region.id)
            });
            navigate(ROUTE_ARTICLE_LIST);
        } catch (error) {
            const message = formatApiError(error, 'Failed to create article');
            setSaveError(message);
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="ArticleCreate">
            <h1>Create Article</h1>
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

export default ArticleCreate;
