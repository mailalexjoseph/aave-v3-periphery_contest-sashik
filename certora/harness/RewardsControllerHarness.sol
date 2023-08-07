// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.10;

import {RewardsController} from '../../contracts/rewards/RewardsController.sol';
import {IScaledBalanceToken} from '@aave/core-v3/contracts/interfaces/IScaledBalanceToken.sol';
import {RewardsDataTypes} from '../../contracts/rewards/libraries/RewardsDataTypes.sol';
contract RewardsControllerHarness is RewardsController {
    
    constructor(address emissionManager) RewardsController(emissionManager) {}
    // returns an asset's reward index
    function getAssetRewardIndex(address asset, address reward) external view returns (uint256) {
        return _assets[asset].rewards[reward].index;
    }

    function authorizedClaimers(address user) external view returns (address) {
        return _authorizedClaimers[user];
    }

    function transferStrategy(address reward) external view returns (address) {
        return address(_transferStrategy[reward]);
    }

    function rewardOracle(address reward) external view returns (address) {
        return address(_rewardOracle[reward]);
    }

    function isContract(address account) external returns (bool) {
        uint256 size;
        assembly { size := extcodesize(account) }
        return size > 0;
    }

    function getRevisionHarness() external pure returns (uint256) {
        return getRevision();
    }

    function isAsset(address asset) external returns (bool) {
        uint256 length = _assetsList.length;
        for (uint256 i; i < length; i++) {
            if (asset == _assetsList[i]) {
                return true;
            }
        }
        return false;
    }

    function getAssetsList() external view returns (address[] memory) {
        return _assetsList;
    }

    function getScaledUserBalanceAndSupply(IScaledBalanceToken asset, address user) external view returns (uint256, uint256) {
        return IScaledBalanceToken(asset).getScaledUserBalanceAndSupply(user);
    }

    function getAccruedRewardsByUser(address asset, address reward, address user) external view returns (uint256) {
        return _assets[asset].rewards[reward].usersData[user].accrued;
    }

    function getUserAssetBalances(address[] calldata assets, address user, uint256 index) external view returns(uint256 balance, uint256 totalSupply) {
        RewardsDataTypes.UserAssetBalance memory res = _getUserAssetBalances(assets, user)[index];
        (balance, totalSupply) = (res.userBalance, res.totalSupply);
    }

    function configureAssetsHarness(uint88[] memory emissionPerSecond, uint256[] memory totalSupply, uint32[] memory distributionEnd, address[] memory asset, address[] memory reward) external onlyEmissionManager {
        RewardsDataTypes.RewardsConfigInput[] memory config = new RewardsDataTypes.RewardsConfigInput[](emissionPerSecond.length);
        for (uint256 i; i < config.length; i++) {
            config[i].emissionPerSecond = emissionPerSecond[i];
            config[i].totalSupply = totalSupply[i];
            config[i].distributionEnd = distributionEnd[i];
            config[i].asset = asset[i];
            config[i].reward = reward[i];
        }

        _configureAssets(config);
    }

    function isRewardEnabled(address reward) external view returns (bool) {
        return _isRewardEnabled[reward];
    }

    function assetScaledTotalSupply(address asset) external view returns (uint256) {
        return IScaledBalanceToken(asset).scaledTotalSupply();
    }

}