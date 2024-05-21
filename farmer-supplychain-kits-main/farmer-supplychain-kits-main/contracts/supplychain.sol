// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract supplychain {
  // retailer products info
  string[] _rproducts;
  string[] _rquantity;
  string[] _rprice;
  uint[] _roderids;
  uint[] _rstatuses;
  string[] _retailers;

  string[] _consumers;
  string[] _cproducts;
  string[] _cquantity;
  string[] _cretailer;
  uint[] _corderids;
  uint[] _cstatuses;

  uint rorderid=0;
  uint corderid=0;

  function raddOrder(string memory retailer,string memory rproduct,string memory rquantity,string memory rprice) public {
    rorderid+=1;
    _retailers.push(retailer);
    _roderids.push(rorderid);
    _rproducts.push(rproduct);
    _rquantity.push(rquantity);
    _rprice.push(rprice);
    _rstatuses.push(0);
  }

  function rviewOrders() public view returns(string[] memory,string[] memory,string[] memory, string[] memory, uint[] memory,uint[] memory) {
    return(_retailers,_rproducts,_rquantity,_rprice,_roderids,_rstatuses); 
  }

  function rupdateOrder(uint orderid,uint status) public {
    uint i;

    for(i=0;i<_roderids.length;i++){
      if (_roderids[i]==orderid){
        _rstatuses[i]=status;
      }
    }
  }

  function caddOrder(string memory cemail,string memory cproduct,string memory cquantity,string memory cretailer) public {
    corderid+=1;
    _consumers.push(cemail);
    _corderids.push(corderid);
    _cproducts.push(cproduct);
    _cquantity.push(cquantity);
    _cretailer.push(cretailer);
    _cstatuses.push(0);
  }

  function cviewOrders() public view returns(string[] memory,string[] memory,string[] memory, string[] memory, uint[] memory,uint[] memory) {
    return(_consumers,_cproducts,_cquantity,_cretailer,_corderids,_cstatuses); 
  }

  function cupdateOrder(uint orderid,uint status) public {
    uint i;

    for(i=0;i<_corderids.length;i++){
      if (_corderids[i]==orderid){
        _cstatuses[i]=status;
      }
    }
  }
}
