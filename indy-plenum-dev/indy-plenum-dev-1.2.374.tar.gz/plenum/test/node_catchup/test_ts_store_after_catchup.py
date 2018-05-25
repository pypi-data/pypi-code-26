from plenum.test.helper import sdk_send_random_and_check
from plenum.test.node_catchup.helper import waitNodeDataEquality
from plenum.test.pool_transactions.helper import disconnect_node_and_ensure_disconnected
from plenum.test.test_node import checkNodesConnected
from plenum.test.view_change.helper import start_stopped_node


def test_fill_ts_store_after_catchup(txnPoolNodeSet,
                                     looper,
                                     sdk_pool_handle,
                                     sdk_wallet_steward,
                                     tconf,
                                     tdir,
                                     allPluginsPath
                                     ):
    sdk_send_random_and_check(looper, txnPoolNodeSet,
                              sdk_pool_handle, sdk_wallet_steward, 5)
    node_to_disconnect = txnPoolNodeSet[-1]

    disconnect_node_and_ensure_disconnected(looper,
                                            txnPoolNodeSet,
                                            node_to_disconnect)
    looper.removeProdable(name=node_to_disconnect.name)
    sdk_replies = sdk_send_random_and_check(looper, txnPoolNodeSet,
                                            sdk_pool_handle, sdk_wallet_steward, 2)

    node_to_disconnect = start_stopped_node(node_to_disconnect, looper, tconf,
                                            tdir, allPluginsPath)
    txnPoolNodeSet[-1] = node_to_disconnect
    looper.run(checkNodesConnected(txnPoolNodeSet))

    waitNodeDataEquality(looper, node_to_disconnect, *txnPoolNodeSet)
    req_handler = node_to_disconnect.getDomainReqHandler()
    for reply in sdk_replies:
        key = req_handler.prepare_buy_key(reply[1]['result']['identifier'],
                                           reply[1]['result']['reqId'])
        root_hash = req_handler.ts_store.get_equal_or_prev(reply[1]['result']['txnTime'])
        assert root_hash
        from_state = req_handler.state.get_for_root_hash(root_hash=root_hash,
                                                         key=key)
        assert req_handler.stateSerializer.deserialize(from_state)['amount'] == \
               reply[1]['result']['amount']
