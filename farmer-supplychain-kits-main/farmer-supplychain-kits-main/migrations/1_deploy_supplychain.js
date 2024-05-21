const supplychain=artifacts.require('supplychain');

module.exports=function(deployer){
    deployer.deploy(supplychain);
}