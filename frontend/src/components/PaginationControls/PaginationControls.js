import React from 'react';
import PropTypes from 'prop-types';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';

const PaginationControls = ({
  pagination,
  onPrev,
  onNext,
  disabled = false,
  className = '',
}) => {
  if (!pagination) {
    return null;
  }

  const {
    current_page: currentPage = 1,
    total_pages: totalPages = 1,
    total_items: totalItems = 0,
    per_page: perPage = 0,
    has_prev: hasPrev = false,
    has_next: hasNext = false,
  } = pagination;

  const upperBound = perPage ? Math.min(totalItems, currentPage * perPage) : totalItems;
  const lowerBound = totalItems === 0 ? 0 : ((currentPage - 1) * perPage) + 1;

  return (
    <div className={`d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3 mt-3 ${className}`}>
      <div className="text-muted">
        Showing {lowerBound || 0}
        {totalItems > 0 && ` - ${upperBound}`} of {totalItems} total
      </div>
      <ButtonGroup>
        <Button
          variant="outline-secondary"
          onClick={ onPrev }
          disabled={ disabled || !hasPrev }
        >
          Previous
        </Button>
        <Button
          variant="outline-secondary"
          onClick={ onNext }
          disabled={ disabled || !hasNext }
        >
          Next
        </Button>
      </ButtonGroup>
      <div className="text-muted">
        Page {currentPage} of {totalPages || 1}
      </div>
    </div>
  );
};

PaginationControls.propTypes = {
  pagination: PropTypes.shape({
    current_page: PropTypes.number,
    total_pages: PropTypes.number,
    total_items: PropTypes.number,
    per_page: PropTypes.number,
    has_prev: PropTypes.bool,
    has_next: PropTypes.bool,
  }),
  onPrev: PropTypes.func.isRequired,
  onNext: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  className: PropTypes.string,
};

export default PaginationControls;
