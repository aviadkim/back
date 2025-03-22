const express = require('express');
const router = express.Router();
const controller = require('./controller');

// GET all items
router.get('/', controller.getAll);

// GET single item by ID
router.get('/:id', controller.getById);

// POST new item
router.post('/', controller.create);

// PUT update item
router.put('/:id', controller.update);

// DELETE item
router.delete('/:id', controller.delete);

module.exports = router;
