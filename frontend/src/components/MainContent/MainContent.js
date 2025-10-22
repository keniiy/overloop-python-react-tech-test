import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Container from 'react-bootstrap/Container';

import {
    ROUTE_HOME,
    ROUTE_ARTICLE_LIST,
    ROUTE_ARTICLE_CREATE,
    ROUTE_ARTICLE_EDIT,
    ROUTE_AUTHOR_LIST,
    ROUTE_AUTHOR_CREATE,
    ROUTE_AUTHOR_EDIT,
    ROUTE_AUTHOR_VIEW,
    ROUTE_ARTICLE_VIEW,
} from '../../constants';
import ArticleList from '../../pages/Articles/ArticleList/ArticleList';
import ArticleCreate from '../../pages/Articles/ArticleCreate/ArticleCreate';
import ArticleEdit from '../../pages/Articles/ArticleEdit/ArticleEdit';
import ArticleView from '../../pages/Articles/ArticleView/ArticleView';
import AuthorList from '../../pages/Authors/AuthorList/AuthorList';
import AuthorCreate from '../../pages/Authors/AuthorCreate/AuthorCreate';
import AuthorEdit from '../../pages/Authors/AuthorEdit/AuthorEdit';
import AuthorView from '../../pages/Authors/AuthorView/AuthorView';

function MainContent() {
    return (
        <div className="MainContent mt-3">
            <Container>
                <Routes>
                    {/* Article routes */}
                    <Route path={ ROUTE_ARTICLE_LIST } element={<ArticleList />} />
                    <Route path={ ROUTE_ARTICLE_CREATE } element={<ArticleCreate />} />
                    <Route path={ ROUTE_ARTICLE_VIEW } element={<ArticleView />} />
                    <Route path={ ROUTE_ARTICLE_EDIT } element={<ArticleEdit />} />
                    
                    {/* Author routes */}
                    <Route path={ ROUTE_AUTHOR_LIST } element={<AuthorList />} />
                    <Route path={ ROUTE_AUTHOR_CREATE } element={<AuthorCreate />} />
                    <Route path={ ROUTE_AUTHOR_VIEW } element={<AuthorView />} />
                    <Route path={ ROUTE_AUTHOR_EDIT } element={<AuthorEdit />} />
                    
                    {/* Default and 404 routes */}
                    <Route path={ ROUTE_HOME } element={<Navigate to={ ROUTE_ARTICLE_LIST } replace />} />
                    <Route path="*" element={<div>404 - Page Not Found</div>} />
                </Routes>
            </Container>
        </div>
    );
}

export default MainContent;
