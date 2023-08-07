import "methods/Methods_base.spec";

///////////////// Properties ///////////////////////

using DummyERC20_rewardToken as rewardToken;
using RewardsControllerHarness as rewardController;
// Checks that claimRewards reverts if destination address is 0
// Catch bug2
rule zeroAddressCheckToClaimRewards() {
    env e;
    address[] assets; 
    uint256 amount;
    address reward;

    claimRewards@withrevert(e, assets, amount, 0, reward);
    assert lastReverted;
}
// Checks that claimRewardsOnBehalf reverts if destination address is 0
rule zeroAddressCheckToClaimRewardsOnBehalf() {
    env e;
    address[] assets; 
    uint256 amount;
    address reward;
    address user;

    claimRewardsOnBehalf@withrevert(e, assets, amount, user, 0, reward);
    assert lastReverted;
}
// Checks that claimRewardsOnBehalf reverts if user address is 0
rule zeroAddressCheckUserClaimRewardsOnBehalf() {
    env e;
    address[] assets; 
    uint256 amount;
    address reward;
    address to;

    claimRewardsOnBehalf@withrevert(e, assets, amount, 0, to, reward);
    assert lastReverted;
}
// Checks that claimAllRewards reverts if destination address is 0
rule zeroAddressCheckToClaimAllRewards() {
    env e;
    address[] assets; 

    claimAllRewards@withrevert(e, assets, 0);
    assert lastReverted;
}
// Checks that claimAllRewardsOnBehalf reverts if destination address is 0
rule zeroAddressCheckToClaimAllRewardsOnBehalf() {
    env e;
    address[] assets; 
    address user;

    claimAllRewardsOnBehalf@withrevert(e, assets, user, 0);
    assert lastReverted;
}
// Checks that claimAllRewardsOnBehalf reverts if user address is 0
rule zeroAddressCheckUserClaimAllRewardsOnBehalf() {
    env e;
    address[] assets; 
    address to;

    claimAllRewardsOnBehalf@withrevert(e, assets, 0, to);
    assert lastReverted;
}
// Checks that getClaimer returns correct address
rule checkGetClaimer() {
    env e;
    address user;
    address exp = authorizedClaimers(e, user);
    address res = getClaimer(e, user);

    assert exp == res;
}
// Checks that getRewardOracle returns correct address
rule checkGetRewardOracle() {
    env e;
    address reward;
    address exp = rewardOracle(e, reward);
    address res = getRewardOracle(e, reward);

    assert exp == res;
}
// Checks that getTransferStrategy returns correct address
rule checkGetTransferStrategy() {
    env e;
    address reward;
    address exp = transferStrategy(e, reward);
    address res = getTransferStrategy(e, reward);

    assert exp == res;
}
// Checks that getRevisionHarness returns correct REVISION value
rule checkGetRevision() {
    env e;
    address reward;
    uint256 exp = REVISION(e);
    uint256 res = getRevisionHarness(e);

    assert exp == res;
}
// Checks that setClaimer sets correct address only by EMISSION_MANAGER
rule correctClaimerSetting() {
    env e;
    address user;
    address claimer;
    
    address EMISSION_MANAGER = EMISSION_MANAGER(e);
    
    address _claimer = getClaimer(e, user);
    setClaimer(e, user, claimer);
    address claimer_ = getClaimer(e, user);
    assert e.msg.sender != EMISSION_MANAGER => _claimer == claimer_;
    assert claimer != _claimer => claimer_ == claimer;
}
// Checks that setTransferStrategy sets correct address only by EMISSION_MANAGER
rule correctTransferStrategySetting() {
    env e;
    address reward;
    address transferStrategy;
    
    address EMISSION_MANAGER = EMISSION_MANAGER(e);
    
    address _transferStrategy = getTransferStrategy(e, reward);
    setTransferStrategy(e, reward, transferStrategy);
    address transferStrategy_ = getTransferStrategy(e, reward);
    assert e.msg.sender != EMISSION_MANAGER || transferStrategy == 0 || !isContract(e, transferStrategy) => _transferStrategy == transferStrategy_;
    assert transferStrategy != _transferStrategy => transferStrategy_ == transferStrategy; 
}
// Checks that setRewardOracle sets correct address only by EMISSION_MANAGER
rule correctRewardOracleSetting() {
    env e;
    address reward;
    address rewardOracle;
    
    address EMISSION_MANAGER = EMISSION_MANAGER(e);
    
    address _rewardOracle = getRewardOracle(e, reward);
    setRewardOracle(e, reward, rewardOracle);
    address rewardOracle_ = getRewardOracle(e, reward);
    assert e.msg.sender != EMISSION_MANAGER => _rewardOracle == rewardOracle_;
    assert rewardOracle != _rewardOracle => rewardOracle_ == rewardOracle; 
}

//TODO check case with 0 totalSupply
// Check that rewards data updates correctly and only by asset address
rule correctHandleAction() {
    env e;
    address user;
    uint256 totalSupply;
    require totalSupply > 0;
    uint256 userBalance;
    require userBalance <= totalSupply;
    uint256 _timestamp;
    uint256 timestamp_;
    address[] assets;
    uint256 amount;
    address to;

    require e.msg.sender == assets[0];
    storage initial = lastStorage;

    address[] rewards = getRewardsByAsset(e, assets[0]);
    require rewards.length == 1;
    require rewards[0] == rewardToken;

    _, _, _timestamp, _ = getRewardsData(e, assets[0], rewardToken);
    require _timestamp <= e.block.timestamp;

    uint256 claimed = claimRewards(e, assets, amount, to, rewardToken);
    require claimed > 0;

    _, _, timestamp_, _ = getRewardsData(e, assets[0], rewardToken);

    require timestamp_ == e.block.timestamp;

    handleAction(e, user, totalSupply, userBalance) at initial;
    uint256 timestamp__;
    _, _, timestamp__, _ = getRewardsData(e, assets[0], rewardToken);

    assert timestamp__ == e.block.timestamp;
}
// Checks that 0 amount claim returns always 0 tokens
rule checkZeroAmount() {
    env e;
    address[] assets;
    uint256 amount = 0;
    address user;
    address to;

    uint256 _timestamp; uint256 timestamp_;

    address[] rewards = getRewardsByAsset(e, assets[0]);
    require rewards.length == 1;
    require rewards[0] == rewardToken;

    _, _, _timestamp, _ = getRewardsData(e, assets[0], rewardToken);
    require _timestamp < e.block.timestamp;

    uint256 claimed = claimRewards(e, assets, amount, to, rewardToken);

    _, _, timestamp_, _ = getRewardsData(e, assets[0], rewardToken);

    assert timestamp_ == _timestamp;
    assert claimed == 0;
}
// Checks that only authorized address could claim on behalf of user
rule checkOnlyAuthorizedClaimersCanClaim() {
    env e;
    address[] assets;
    uint256 amount;
    address user;
    address to;
    address reward;

    require getClaimer(user) != e.msg.sender;

    claimRewardsOnBehalf@withrevert(e, assets, amount, user, to, reward);
    assert lastReverted;
}
// Checks that only authorized address could claim all on behalf of user
rule checkOnlyAuthorizedClaimersCanClaimAll() {
    env e;
    address[] assets;
    address user;
    address to;

    require getClaimer(user) != e.msg.sender;

    claimAllRewardsOnBehalf@withrevert(e, assets, user, to);
    assert lastReverted;
}
// Check that _getUserAssetBalances return correct value 
rule checkGetUserBalances() {
    env e;
    address[] assets;
    address user;
    uint256 _balance; uint256 balance_;
    uint256 _totalSupply; uint256 totalSupply_;

    _balance, _totalSupply = getScaledUserBalanceAndSupply(e, assets[0], user);
    balance_, totalSupply_ = getUserAssetBalances(e, assets, user, 0);

    assert _balance == balance_ && _totalSupply == totalSupply_;
}
// Checks that claimRewards claim correct amount of tokens and update reward data 
// Catch bug1
rule checkClaimRewards() {
    env e;
    address[] assets;
    uint256 amount;
    address user;
    address to;
    address strategy = getTransferStrategy(e, rewardToken);
    require to != strategy;

    uint256 _timestamp; uint256 timestamp_;

    address[] rewards = getRewardsByAsset(e, assets[0]);
    require rewards.length == 1;
    require rewards[0] == rewardToken;

    address[] assetList = getAssetsList(e);
    require assetList.length == 1;
    require assets.length == 1;

    _, _, _timestamp, _ = getRewardsData(e, assets[0], rewardToken);
    require _timestamp < e.block.timestamp;
    uint256 _balanceTo = rewardToken.balanceOf(e, to);
    uint256 _balanceStrategy = rewardToken.balanceOf(e, strategy);
    uint256 _totalRewards = getUserRewards(e, assets, e.msg.sender, rewardToken);

    uint256 claimed = claimRewards(e, assets, amount, to, rewardToken);
    require claimed > 0;

    _, _, timestamp_, _ = getRewardsData(e, assets[0], rewardToken);
    uint256 balanceTo_ = rewardToken.balanceOf(e, to);
    uint256 balanceStrategy_ = rewardToken.balanceOf(e, strategy);
    uint256 accrued_ = getAccruedRewardsByUser(e, assets[0], rewardToken, e.msg.sender);

    assert timestamp_ == e.block.timestamp;
    assert assert_uint256(balanceTo_ - _balanceTo) == claimed && assert_uint256(_balanceStrategy - balanceStrategy_) == claimed;

    if (amount > _totalRewards) {
        assert accrued_ == 0;
    } else {
        assert accrued_ == assert_uint256(_totalRewards - amount);
    }
}
// Checks that claimRewardsOnBehalf claim correct amount of tokens
rule checkClaimRewardsOnBehalf() {
    env e;
    address[] assets;
    uint256 amount;
    address user;
    address to;
    address strategy = getTransferStrategy(e, rewardToken);
    require to != strategy;

    uint256 _totalRewards = getUserRewards(e, assets, user, rewardToken);
    uint256 _balanceTo = rewardToken.balanceOf(e, to);

    uint256 claimed = claimRewardsOnBehalf(e, assets, _totalRewards, user, to, rewardToken);
    require claimed == _totalRewards;

    uint256 balanceTo_ = rewardToken.balanceOf(e, to);
    assert assert_uint256(balanceTo_ - _balanceTo) == claimed;
}
// Checks that claimRewardsToSelf claim correct amount of tokens
rule checkClaimRewardsToSelf() {
    env e;
    address[] assets;
    uint256 amount;
    address strategy = getTransferStrategy(e, rewardToken);
    require e.msg.sender != strategy;

    uint256 _totalRewards = getUserRewards(e, assets, e.msg.sender, rewardToken);
    uint256 _balanceTo = rewardToken.balanceOf(e, e.msg.sender);

    uint256 claimed = claimRewardsToSelf(e, assets, _totalRewards, rewardToken);
    require claimed == _totalRewards;

    uint256 balanceTo_ = rewardToken.balanceOf(e, e.msg.sender);
    assert assert_uint256(balanceTo_ - _balanceTo) == claimed;
}
// Checks that claimAllRewards claim correct amount of tokens and update reward data 
// Catch bug3
rule checkClaimAllRewards() {
    env e;
    address[] assets;
    uint256 amount;
    address user;
    address to;
    address strategy = getTransferStrategy(e, rewardToken);
    require to != strategy;

    uint256 _timestamp; uint256 timestamp_;

    address[] rewards = getRewardsByAsset(e, assets[0]);
    require rewards.length == 1;
    require rewards[0] == rewardToken;
    
    address[] rewardsList = getRewardsList(e);
    require rewardsList.length == 1;
    require rewardsList[0] == rewardToken;

    address[] assetList = getAssetsList(e);
    require assetList.length == 1;
    require assets.length == 1;

    _, _, _timestamp, _ = getRewardsData(e, assets[0], rewardToken);
    require _timestamp < e.block.timestamp;
    uint256 _balanceTo = rewardToken.balanceOf(e, to);
    uint256 _balanceStrategy = rewardToken.balanceOf(e, strategy);
    uint256 _totalRewards = getUserRewards(e, assets, e.msg.sender, rewardToken);

    uint256[] claimedAmounts;
    _, claimedAmounts = claimAllRewards(e, assets, to);
    require claimedAmounts[0] > 0;

    _, _, timestamp_, _ = getRewardsData(e, assets[0], rewardToken);
    uint256 balanceTo_ = rewardToken.balanceOf(e, to);
    uint256 balanceStrategy_ = rewardToken.balanceOf(e, strategy);
    uint256 accrued_ = getAccruedRewardsByUser(e, assets[0], rewardToken, e.msg.sender);

    assert timestamp_ == e.block.timestamp;
    assert assert_uint256(balanceTo_ - _balanceTo) == claimedAmounts[0] && assert_uint256(_balanceStrategy - balanceStrategy_) == claimedAmounts[0];

    assert accrued_ == 0;
}
// Checks that claimAllRewardsOnBehalf claim correct amount of tokens
rule checkClaimAllRewardsOnBehalf() {
    env e;
    address[] assets;
    uint256 amount;
    address user;
    address to;
    address strategy = getTransferStrategy(e, rewardToken);
    require to != strategy;

    address[] rewardsList = getRewardsList(e);
    require rewardsList.length == 1;
    require rewardsList[0] == rewardToken;

    uint256 _totalRewards = getUserRewards(e, assets, user, rewardToken);
    uint256 _balanceTo = rewardToken.balanceOf(e, to);

    uint256[] claimedAmounts;
    _, claimedAmounts = claimAllRewardsOnBehalf(e, assets, user, to);
    require claimedAmounts[0] == _totalRewards;

    uint256 balanceTo_ = rewardToken.balanceOf(e, to);
    assert assert_uint256(balanceTo_ - _balanceTo) == _totalRewards;
}
// Checks that claimAllRewardsToSelf claim correct amount of tokens
rule checkClaimAllRewardsToSelf() {
    env e;
    address[] assets;
    uint256 amount;
    address strategy = getTransferStrategy(e, rewardToken);
    require e.msg.sender != strategy;

    address[] rewardsList = getRewardsList(e);
    require rewardsList.length == 1;
    require rewardsList[0] == rewardToken;

    uint256 _totalRewards = getUserRewards(e, assets, e.msg.sender, rewardToken);
    uint256 _balanceTo = rewardToken.balanceOf(e, e.msg.sender);

    uint256[] claimedAmounts;
    _, claimedAmounts = claimAllRewardsToSelf(e, assets);
    require claimedAmounts[0] == _totalRewards;

    uint256 balanceTo_ = rewardToken.balanceOf(e, e.msg.sender);
    assert assert_uint256(balanceTo_ - _balanceTo) == _totalRewards;
}
// Checks that configureAssets update assetsList, rewardsList and transfer strategies
rule checkConfireAssets() {
    env e;
    calldataarg args;
    address EMISSION_MANAGER = EMISSION_MANAGER(e);

    address[] _assetsList = getAssetsList(e);
    require _assetsList.length == 0;
    address[] _rewardsList = getRewardsList(e);
    require _rewardsList.length == 0;

    configureAssets(e, args);

    address[] assetsList_ = getAssetsList(e);
    address[] rewardsList_ = getRewardsList(e);

    require assetsList_.length > 1 && rewardsList_.length > 1;
    assert e.msg.sender == EMISSION_MANAGER;

    address transferStrategyOne = getTransferStrategy(e, rewardsList_[0]);
    address transferStrategyTwo = getTransferStrategy(e, rewardsList_[1]);
    assert transferStrategyOne != 0 && transferStrategyTwo != 0;

}
// Check that claimRewards work correcly if amount > claimable rewards
rule checkClaimRewardsOnBiggerAmount() {
    env e;
    address[] assets;
    uint256 amount;
    address user;
    address to;

    uint256 _timestamp; uint256 timestamp_;

    address[] rewards = getRewardsByAsset(e, assets[0]);
    require rewards.length == 1;
    require rewards[0] == rewardToken;

    address[] assetList = getAssetsList(e);
    require assetList.length == 1;
    require assets.length == 1;

    _, _, _timestamp, _ = getRewardsData(e, assets[0], rewardToken);
    require _timestamp < e.block.timestamp;

    uint256 _totalRewards = getUserRewards(e, assets, e.msg.sender, rewardToken);
    require amount > _totalRewards;

    uint256 claimed = claimRewards(e, assets, amount, to, rewardToken);
    require claimed > 0;

    _, _, timestamp_, _ = getRewardsData(e, assets[0], rewardToken);
    uint256 accrued_ = getAccruedRewardsByUser(e, assets[0], rewardToken, e.msg.sender);

    assert timestamp_ == e.block.timestamp;
    assert accrued_ == 0;
}
// Checks that claimAllRewards claims correct amount of tokens and update reward data
rule checkClaimAllRewardsCorrectAmount() {
    env e;
    address[] assets;
    require assets.length == 1;
    uint256 amount;
    address user;
    address to;

    uint256 _timestamp; uint256 timestamp_;

    address[] rewards = getRewardsByAsset(e, assets[0]);
    require rewards.length == 1;
    require rewards[0] == rewardToken;
    
    address[] rewardsList = getRewardsList(e);
    require rewardsList.length == 1;
    require rewardsList[0] == rewardToken;

    address[] assetList = getAssetsList(e);
    require assetList.length == 1;
    require assets.length == 1;

    _, _, _timestamp, _ = getRewardsData(e, assets[0], rewardToken);
    require _timestamp < e.block.timestamp;

    uint256 _totalRewards = getUserRewards(e, assets, e.msg.sender, rewardToken);

    uint256[] claimedAmounts;
    _, claimedAmounts = claimAllRewards(e, assets, to);
    require claimedAmounts[0] > 0;

    _, _, timestamp_, _ = getRewardsData(e, assets[0], rewardToken);

    assert timestamp_ == e.block.timestamp;
    assert claimedAmounts[0] == _totalRewards;
}
// Checks that configureAssets get correct totalSupply 
rule correctTotalSupplyConfigured() {
    env e;
    calldataarg args;

    address[] _assetsList = getAssetsList(e);
    require _assetsList.length == 0;
    address[] _rewardsList = getRewardsList(e);
    require _rewardsList.length == 0;

    configureAssets(e, args);

    address[] assetsList_ = getAssetsList(e);
    address[] rewardsList_ = getRewardsList(e);
    require assetsList_.length == 1 && rewardsList_.length == 1;

    uint256 oldIndex; uint256 newIndex;
    oldIndex, newIndex = getAssetIndex(e, assetsList_[0], rewardsList_[0]);
    assert oldIndex == newIndex;
}
// Checks that not possible to claim two times in a row
rule noDoubleClaimAllRewards() {
    env e;
    address[] assets;
    address to;

    address[] _assetsList = getAssetsList(e);
    require _assetsList.length == 1;
    address[] _rewardsList = getRewardsList(e);
    require _rewardsList.length == 1;

    uint256[] _claimedAmounts;
    _, _claimedAmounts = claimAllRewards(e, assets, to);
    require _claimedAmounts[0] != 0;

    uint256[] claimedAmounts_;
    _, claimedAmounts_ = claimAllRewards(e, assets, to);
    assert claimedAmounts_[0] == 0;
}
// Checks that claim rewards update correct amount of accrued tokens 
rule checkClaimRewardsCorrectAccrued() {
    env e;
    address[] assets;
    uint256 amount;
    address user;
    address to;

    uint256 _timestamp; uint256 timestamp_;

    address[] rewards = getRewardsByAsset(e, assets[0]);
    require rewards.length == 1;
    require rewards[0] == rewardToken;

    address[] assetList = getAssetsList(e);
    require assetList.length == 1;
    require assets.length == 1;

    _, _, _timestamp, _ = getRewardsData(e, assets[0], rewardToken);
    require _timestamp < e.block.timestamp;

    uint256 _totalRewards = getUserRewards(e, assets, e.msg.sender, rewardToken);
    require amount < _totalRewards;

    uint256 claimed = claimRewards(e, assets, amount, to, rewardToken);
    require claimed > 0;

    _, _, timestamp_, _ = getRewardsData(e, assets[0], rewardToken);
    uint256 accrued_ = getAccruedRewardsByUser(e, assets[0], rewardToken, e.msg.sender);

    assert timestamp_ == e.block.timestamp;
    assert accrued_ == assert_uint256(_totalRewards - amount);
    assert claimed == amount;
}
// Checks that setEmissions reverts in correct cases 
rule checkSetEmissionRevert() {
    env e;
    address asset;
    address[] rewards;
    uint88[] newEmissions;
    uint256 lastUpdated;
    require newEmissions[0] < 309485009821345068724781055;
    uint256 nexIndex;
    _, nexIndex = getAssetIndex(e, asset, rewards[0]);
    require nexIndex <= 20282409603651670423947251286015;

    require rewards.length == 1;
    require e.msg.value == 0;
    require e.msg.sender == EMISSION_MANAGER(e);
    require e.block.timestamp < 4294967295;

    uint256 decimals = getAssetDecimals(e, asset);
    _, _, lastUpdated, _ = getRewardsData(e, asset, rewards[0]);

    setEmissionPerSecond@withrevert(e, asset, rewards, newEmissions);
    assert lastReverted <=> (rewards.length != newEmissions.length || decimals == 0 || lastUpdated == 0);
}
// Checks that setEmissions sets correct emission rate 
rule checkSetEmison() {
    env e;
    address asset;
    address[] rewards;
    uint88[] newEmissions;
    require rewards.length == 2;
    uint256 _oldIndex; uint256 _newIndex; uint256 oldIndex_; uint256 newIndex_;
    uint256 decimals = getAssetDecimals(e, asset);
    require decimals == 18;
    _oldIndex, _newIndex = getAssetIndex(e, asset, rewards[1]);
    require _oldIndex < _newIndex;
    setEmissionPerSecond(e, asset, rewards, newEmissions);
    uint256 emission;
    _, emission, _, _ = getRewardsData(e, asset, rewards[1]);
    assert newEmissions[1] == assert_uint88(emission);
    oldIndex_, newIndex_ = getAssetIndex(e, asset, rewards[1]);
    assert oldIndex_ == newIndex_;
}
// Checks that configureAssets correctly updates asset params
rule checkConfireAssetsInternal() {
    env e;
    uint88[] emissionsPerSecond;
    uint256[] totalSupplys;
    uint32[] distributionEnds;
    address[] assets;
    address[] rewards;

    require e.block.timestamp > 0;

    address[] _rewardsByAsset;
    _rewardsByAsset = getRewardsByAsset(e, assets[0]);
    require _rewardsByAsset.length == 0;
    address[] assetsList_ = getAssetsList(e);
    require assetsList_.length == 0;
    address[] rewardsList_ = getRewardsList(e);
    require rewardsList_.length == 0;

    require !isRewardEnabled(e, rewards[0]);

    uint256 _emissionPerSecond; uint256 _lastUpdateTimestamp; uint256 _distributionEnd;
    _, _emissionPerSecond, _lastUpdateTimestamp, _distributionEnd = getRewardsData(assets[0], rewards[0]);
    require _emissionPerSecond == 0; 
    require _lastUpdateTimestamp == 0;
    require _distributionEnd == 0;

    configureAssetsHarness(e, emissionsPerSecond, totalSupplys, distributionEnds, assets, rewards);

    address[] rewardsByAsset_;
    rewardsByAsset_ = getRewardsByAsset(e, assets[0]);
    require rewardsByAsset_.length > 0;
    address[] _assetsList = getAssetsList(e);
    require _assetsList.length > 0;
    address[] _rewardsList = getRewardsList(e);
    require _rewardsList.length > 0;

    require isRewardEnabled(e, rewards[0]);

    uint256 emissionPerSecond_; uint256 lastUpdateTimestamp_; uint256 distributionEnd_;
    _, emissionPerSecond_, lastUpdateTimestamp_, distributionEnd_ = getRewardsData(assets[0], rewards[0]);
    require emissionPerSecond_ > 0; 
    require lastUpdateTimestamp_ == e.block.timestamp;
    require distributionEnd_ > 0;

    assert true;
}
// Checks that number of assets increase by one 
rule checkConfireAssetsIncrease() {
    env e;
    uint88[] emissionsPerSecond;
    uint256[] totalSupplys;
    uint32[] distributionEnds;
    address[] assets;
    address[] rewards;

    require emissionsPerSecond.length == 1;

    address[] _rewardsByAsset;
    _rewardsByAsset = getRewardsByAsset(e, assets[0]);
    require _rewardsByAsset.length == 0;

    configureAssetsHarness(e, emissionsPerSecond, totalSupplys, distributionEnds, assets, rewards);

    address[] rewardsByAsset_;
    rewardsByAsset_ = getRewardsByAsset(e, assets[0]);
    require rewardsByAsset_.length == 1;

    assert true;
}
// Checks that getAllUserRewards returns correct amounts 
rule checkGetAllUserRewards() {
    env e; 
    address user;

    address[] assets = getAssetsList(e);
    require assets.length == 1;
    address[] _rewardsList = getRewardsList(e);
    require _rewardsList.length == 1;

    uint256 balance;
    balance, _ = getUserAssetBalances(e, assets, user, 0);
    require balance > 0;

    uint256 _unclaimedAmounts; 
    _unclaimedAmounts = getUserRewards(e, assets, user, _rewardsList[0]);

    uint256[] unclaimedAmounts_;
    _, unclaimedAmounts_ = getAllUserRewards(e, assets, user);

    assert _rewardsList.length == unclaimedAmounts_.length;
    assert _unclaimedAmounts == unclaimedAmounts_[0];
}

rule checkGetUserAccruedRewards() {
    env e; 
    address user;
    address reward;

    address[] assets = getAssetsList(e);
    require assets.length == 2;
    mathint _accrued;

    _accrued = getAccruedRewardsByUser(e, assets[0], reward, user) + getAccruedRewardsByUser(e, assets[1], reward, user);

    uint256 accrued_ = getUserAccruedRewards(e, user, reward);
    assert assert_uint256(_accrued) == accrued_;
}

// rule checkGetAssetIndex() {
//     env e;
//     address[] assets = getAssetsList(e);
//     require assets.length == 1;
//     address[] _rewardsList = getRewardsList(e);
//     require _rewardsList.length == 1;
//     uint256 _oldIndex; mathint _newIndex;

//     uint256 index; uint256 emissionPerSecond; uint256 lastUpdateTimestamp; uint256 distributionEnd;
//     index, emissionPerSecond, lastUpdateTimestamp, distributionEnd = getRewardsData(e, assets[0], _rewardsList[0]);
//     uint256 totalSupply = assetScaledTotalSupply(e, assets[0]);
//     require totalSupply > 0;
//     uint256 decimals = getAssetDecimals(e, assets[0]);
//     require decimals > 0;

//     _oldIndex = index; 
//     if (emissionPerSecond == 0 || totalSupply == 0 ||
//       lastUpdateTimestamp == e.block.timestamp || lastUpdateTimestamp >= distributionEnd) {
//         _newIndex = index;
//     } else {
//         uint256 time;
//         if (e.block.timestamp > distributionEnd) {
//             time = distributionEnd;
//         } else {
//             time = e.block.timestamp;
//         }
//         _newIndex = index + (emissionPerSecond * (10 ^ decimals) * (time - lastUpdateTimestamp)) / totalSupply;
//     }

//     uint256 oldIndex_; uint256 newIndex_;
//     oldIndex_, newIndex_ = getAssetIndex(e, assets[0], _rewardsList[0]);

//     assert oldIndex_ == _oldIndex && newIndex_ == assert_uint256(_newIndex);
// }