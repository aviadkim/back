// TODO: Replace with actual database model
const items = [];
let nextId = 1;

exports.getAll = async () => {
  return [...items];
};

exports.getById = async (id) => {
  return items.find(item => item.id === parseInt(id));
};

exports.create = async (data) => {
  const newItem = {
    id: nextId++,
    ...data,
    createdAt: new Date().toISOString()
  };
  
  items.push(newItem);
  return newItem;
};

exports.update = async (id, data) => {
  const index = items.findIndex(item => item.id === parseInt(id));
  
  if (index === -1) {
    return null;
  }
  
  const updatedItem = {
    ...items[index],
    ...data,
    updatedAt: new Date().toISOString()
  };
  
  items[index] = updatedItem;
  return updatedItem;
};

exports.delete = async (id) => {
  const index = items.findIndex(item => item.id === parseInt(id));
  
  if (index === -1) {
    return false;
  }
  
  items.splice(index, 1);
  return true;
};
