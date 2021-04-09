

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";

contract FriendlyWager {

    AggregatorV3Interface internal priceFeed;
    
    address payable public creator;
    address payable public accepter;
    int public strike_price;
    uint256 public claim_date;
    bool public creator_is_long; //if true, then accepter is short...
    //int public amount;  //TODO

    /**
     * Network: Kovan
     * Aggregator: ETH/USD
     * Address: 0x9326BFA02ADD2366b30bacB125260Af641031331
     */
    constructor(address AggregatorAddress, address payable _creator, address payable _accepter, int _strike_price, uint256 _claim_date, bool _creator_is_long) public {

        priceFeed = AggregatorV3Interface(AggregatorAddress);
        creator = _creator;
        accepter = _accepter;
        strike_price = _strike_price;
        claim_date = _claim_date;
        creator_is_long = _creator_is_long;
    }

    /**
     * Returns the latest price
     */
    function getLatestPrice() public view returns (int) {
        (
            uint80 roundID, 
            int price,
            uint startedAt,
            uint timeStamp,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        return price;
    }
    
    
    function claim() public returns (int)  {
        //1. check if today is claim_date, bail if not:
        if (now >= claim_date && now < claim_date+86400)  {
        
           //2. get latest price of asset:
           (
            uint80 roundID, 
            int price,
            uint startedAt,
            uint timeStamp,
            uint80 answeredInRound
           ) = priceFeed.latestRoundData();
           
           //3. if creator_is_long and latest_price > strike_price, then send monies to creator, otherwise to accepter:
           if (creator_is_long && price > strike_price)  {
               creator.transfer(address(this).balance);
               return 0;
           } else {
               accepter.transfer(address(this).balance);
               return 0;
           }
        }   
        
        //TODO: refund money if the wager is expired ...

        return 1; //error
    }
    
    function getNow() public view returns (uint256)  {
        return now;
    }
    
    //Note: This is required...
    receive() external payable {
            // TODO: React to receiving ether
    }

}

//TODO: implement modifiers (access modifiers)
