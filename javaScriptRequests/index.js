var Web3 = require('web3');
var provider = 'https://green-spring-brook.quiknode.pro/cfde76e7501da4b8c1b989614be0aad44b393a75/';
var web3Provider = new Web3.providers.HttpProvider(provider);
var web3 = new Web3(web3Provider);
web3.eth.getTransactionReceipt("0x3081a4ac6666e748fee8bc216b86c47c91c43dfd1172b199e3138558964b9004").then((result) => {
  console.log("Block number is ", result["blockNumber"]);
});