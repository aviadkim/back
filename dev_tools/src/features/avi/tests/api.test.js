const request = require('supertest');
const express = require('express');
const router = require('../api/routes');

// Create test app
const app = express();
app.use(express.json());
app.use('/api/avi', router);

describe('avi API', () => {
  it('GET / should return all items', async () => {
    const res = await request(app).get('/api/avi');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBeTruthy();
  });

  it('POST / should create a new item', async () => {
    const newItem = {
      name: 'Test Item',
      description: 'This is a test item'
    };
    
    const res = await request(app)
      .post('/api/avi')
      .send(newItem);
    
    expect(res.statusCode).toEqual(201);
    expect(res.body).toHaveProperty('id');
    expect(res.body.name).toEqual(newItem.name);
  });

  it('GET /:id should return a single item', async () => {
    // First create an item
    const newItem = { name: 'Get Test' };
    const createRes = await request(app)
      .post('/api/avi')
      .send(newItem);
    
    const id = createRes.body.id;
    
    // Then get the item
    const getRes = await request(app).get(`/api/avi/${id}`);
    
    expect(getRes.statusCode).toEqual(200);
    expect(getRes.body.id).toEqual(id);
  });

  it('PUT /:id should update an item', async () => {
    // First create an item
    const newItem = { name: 'Update Test' };
    const createRes = await request(app)
      .post('/api/avi')
      .send(newItem);
    
    const id = createRes.body.id;
    const updateData = { name: 'Updated Name' };
    
    // Then update the item
    const updateRes = await request(app)
      .put(`/api/avi/${id}`)
      .send(updateData);
    
    expect(updateRes.statusCode).toEqual(200);
    expect(updateRes.body.name).toEqual(updateData.name);
  });

  it('DELETE /:id should delete an item', async () => {
    // First create an item
    const newItem = { name: 'Delete Test' };
    const createRes = await request(app)
      .post('/api/avi')
      .send(newItem);
    
    const id = createRes.body.id;
    
    // Then delete the item
    const deleteRes = await request(app).delete(`/api/avi/${id}`);
    expect(deleteRes.statusCode).toEqual(204);
    
    // Try to get the deleted item
    const getRes = await request(app).get(`/api/avi/${id}`);
    expect(getRes.statusCode).toEqual(404);
  });
});
