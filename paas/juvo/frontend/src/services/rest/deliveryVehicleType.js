import request from '../request';

const deliveryVehicleTypeService = {
  getAll: () => request.get('rest/delivery-vehicle-types'),
  getRetailTypes: () => request.get('rest/delivery-vehicle-types?type=retail'),
  getAgricultureTypes: () => request.get('rest/delivery-vehicle-types?type=agriculture'),
};

export default deliveryVehicleTypeService;